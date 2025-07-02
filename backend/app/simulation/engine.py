import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import uuid
import json

from app.core.database import get_db
from app.models.simulation import SimulationState, SimulationEvent
from app.agents.manager import AgentManager
from app.core.config import settings

logger = structlog.get_logger()

class SimulationEngine:
    """Main simulation engine that manages the 15-minute tick simulation loop"""
    
    def __init__(self):
        self.is_running_flag = False
        self.is_paused = False
        self.current_time = datetime.utcnow()
        self.tick_count = 0
        self.speed_multiplier = 1.0
        self.agent_manager = AgentManager()
        self.simulation_task = None
        self.tick_interval = settings.SIMULATION_TICK_INTERVAL  # 15 minutes in seconds
        
        # Simulation state tracking
        self.active_orders = 0
        self.active_deliveries = 0
        self.available_vehicles = 0
        self.total_inventory_items = 0
        self.system_health = "healthy"
        
        # Event tracking
        self.events_processed = 0
        self.agents_active = 0
        
    async def start(self):
        """Start the simulation"""
        if self.is_running_flag:
            logger.warning("Simulation is already running")
            return
        
        logger.info("Starting simulation engine")
        self.is_running_flag = True
        self.is_paused = False
        
        # Initialize simulation state
        await self._initialize_simulation_state()
        
        # Start the simulation loop
        self.simulation_task = asyncio.create_task(self._simulation_loop())
        
        logger.info("Simulation engine started successfully")
    
    async def stop(self):
        """Stop the simulation"""
        if not self.is_running_flag:
            logger.warning("Simulation is not running")
            return
        
        logger.info("Stopping simulation engine")
        self.is_running_flag = False
        
        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                await self.simulation_task
            except asyncio.CancelledError:
                pass
        
        # Save final simulation state
        await self._save_simulation_state()
        
        logger.info("Simulation engine stopped successfully")
    
    async def pause(self):
        """Pause the simulation"""
        if not self.is_running_flag:
            logger.warning("Simulation is not running")
            return
        
        logger.info("Pausing simulation")
        self.is_paused = True
    
    async def resume(self):
        """Resume the simulation"""
        if not self.is_running_flag:
            logger.warning("Simulation is not running")
            return
        
        logger.info("Resuming simulation")
        self.is_paused = False
    
    async def reset(self):
        """Reset the simulation to initial state"""
        logger.info("Resetting simulation")
        
        # Stop current simulation
        if self.is_running_flag:
            await self.stop()
        
        # Reset simulation state
        self.current_time = datetime.utcnow()
        self.tick_count = 0
        self.active_orders = 0
        self.active_deliveries = 0
        self.available_vehicles = 0
        self.total_inventory_items = 0
        self.system_health = "healthy"
        self.events_processed = 0
        self.agents_active = 0
        
        # Clear simulation data from database
        await self._clear_simulation_data()
        
        # Reinitialize simulation state
        await self._initialize_simulation_state()
        
        logger.info("Simulation reset successfully")
    
    def is_running(self) -> bool:
        """Check if simulation is running"""
        return self.is_running_flag and not self.is_paused
    
    def get_current_time(self) -> str:
        """Get current simulation time"""
        return self.current_time.isoformat()
    
    def get_tick_count(self) -> int:
        """Get current tick count"""
        return self.tick_count
    
    def get_speed_multiplier(self) -> float:
        """Get current speed multiplier"""
        return self.speed_multiplier
    
    def set_speed_multiplier(self, multiplier: float):
        """Set simulation speed multiplier"""
        self.speed_multiplier = max(0.1, min(10.0, multiplier))
        logger.info(f"Simulation speed set to {self.speed_multiplier}x")
    
    def get_total_agents(self) -> int:
        """Get total number of agents"""
        return len(self.agent_manager.get_active_agents())
    
    async def _simulation_loop(self):
        """Main simulation loop that runs every tick"""
        logger.info("Starting simulation loop")
        
        while self.is_running_flag:
            try:
                if not self.is_paused:
                    # Process one simulation tick
                    await self._process_tick()
                    
                    # Advance simulation time
                    self.current_time += timedelta(minutes=15)
                    self.tick_count += 1
                    
                    # Calculate sleep time based on speed multiplier
                    sleep_time = self.tick_interval / self.speed_multiplier
                    await asyncio.sleep(sleep_time)
                else:
                    # When paused, just wait a bit
                    await asyncio.sleep(1)
                    
            except asyncio.CancelledError:
                logger.info("Simulation loop cancelled")
                break
            except Exception as e:
                logger.error("Error in simulation loop", error=str(e))
                self.system_health = "error"
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info("Simulation loop ended")
    
    async def _process_tick(self):
        """Process one simulation tick"""
        tick_start = datetime.utcnow()
        events_this_tick = 0
        
        try:
            logger.info(f"Processing simulation tick {self.tick_count}", 
                       simulation_time=self.current_time.isoformat())
            
            # Update system state
            await self._update_system_state()
            
            # Run all agents
            active_agents = await self._run_agents()
            self.agents_active = len(active_agents)
            
            # Process events
            events_this_tick = await self._process_events()
            self.events_processed += events_this_tick
            
            # Save tick data
            await self._save_tick_data(events_this_tick)
            
            # Update simulation state
            await self._save_simulation_state()
            
            tick_duration = (datetime.utcnow() - tick_start).total_seconds()
            logger.info(f"Tick {self.tick_count} completed", 
                       duration_seconds=tick_duration,
                       events_processed=events_this_tick,
                       agents_active=self.agents_active)
            
        except Exception as e:
            logger.error(f"Error processing tick {self.tick_count}", error=str(e))
            self.system_health = "error"
    
    async def _run_agents(self) -> List[str]:
        """Run all active agents for this tick"""
        active_agents = []
        
        try:
            # Get all active agents from the agent manager
            agents = self.agent_manager.get_active_agents()
            
            # Run each agent
            for agent_id in agents:
                try:
                    await self.agent_manager.run_agent_cycle(agent_id)
                    active_agents.append(agent_id)
                except Exception as e:
                    logger.error(f"Error running agent {agent_id}", error=str(e))
            
            return active_agents
            
        except Exception as e:
            logger.error("Error running agents", error=str(e))
            return []
    
    async def _process_events(self) -> int:
        """Process simulation events for this tick"""
        events_processed = 0
        
        try:
            # Generate new orders (simulate customer demand)
            new_orders = await self._generate_orders()
            events_processed += new_orders
            
            # Process deliveries
            completed_deliveries = await self._process_deliveries()
            events_processed += completed_deliveries
            
            # Update inventory
            inventory_updates = await self._update_inventory()
            events_processed += inventory_updates
            
            # Update vehicle positions
            vehicle_updates = await self._update_vehicle_positions()
            events_processed += vehicle_updates
            
            return events_processed
            
        except Exception as e:
            logger.error("Error processing events", error=str(e))
            return 0
    
    async def _generate_orders(self) -> int:
        """Generate new orders based on demand forecast"""
        # This would integrate with the forecasting engine
        # For now, generate a small number of random orders
        import random
        
        orders_generated = random.randint(0, 3)
        if orders_generated > 0:
            logger.info(f"Generated {orders_generated} new orders")
        
        return orders_generated
    
    async def _process_deliveries(self) -> int:
        """Process ongoing deliveries"""
        # This would check delivery status and update as needed
        # For now, return a placeholder
        return 0
    
    async def _update_inventory(self) -> int:
        """Update inventory levels"""
        # This would update inventory based on orders and restocking
        # For now, return a placeholder
        return 0
    
    async def _update_vehicle_positions(self) -> int:
        """Update vehicle positions based on routes"""
        # This would update vehicle locations based on active routes
        # For now, return a placeholder
        return 0
    
    async def _update_system_state(self):
        """Update system state metrics"""
        async for db in get_db():
            try:
                # Count active orders
                from app.models.merchant import Order
                self.active_orders = db.query(Order).filter(
                    Order.status.in_(["pending", "processing", "shipped"])
                ).count()
                
                # Count active deliveries
                from app.models.fleet import Delivery
                self.active_deliveries = db.query(Delivery).filter(
                    Delivery.status.in_(["pending", "in_transit"])
                ).count()
                
                # Count available vehicles
                from app.models.fleet import Vehicle
                self.available_vehicles = db.query(Vehicle).filter(
                    Vehicle.status == "available"
                ).count()
                
                # Count total inventory items
                from app.models.inventory import InventoryItem
                self.total_inventory_items = db.query(InventoryItem).count()
                
            except Exception as e:
                logger.error("Error updating system state", error=str(e))
    
    async def _save_tick_data(self, events_processed: int):
        """Save tick data to database"""
        async for db in get_db():
            try:
                # Create a simulation event for this tick
                tick_event = SimulationEvent(
                    tick_number=self.tick_count,
                    event_type='tick_end',
                    event_data={
                        'agents_active': self.agents_active,
                        'events_processed': events_processed,
                        'simulation_time': self.current_time.isoformat()
                    }
                )
                
                db.add(tick_event)
                await db.commit()
                
            except Exception as e:
                logger.error("Error saving tick data", error=str(e))
                await db.rollback()
    
    async def _save_simulation_state(self):
        """Save current simulation state to database"""
        async for db in get_db():
            try:
                # Update existing state or create new one
                state = db.query(SimulationState).first()
                if not state:
                    state = SimulationState()
                    db.add(state)
                
                # Update state fields
                state.status = 'running' if self.is_running_flag else 'stopped'
                state.current_tick = self.tick_count
                state.speed_multiplier = self.speed_multiplier
                state.config = {
                    'active_orders': self.active_orders,
                    'active_deliveries': self.active_deliveries,
                    'available_vehicles': self.available_vehicles,
                    'total_inventory_items': self.total_inventory_items,
                    'system_health': self.system_health,
                    'agents_active': self.agents_active,
                    'events_processed': self.events_processed
                }
                
                await db.commit()
                
            except Exception as e:
                logger.error("Error saving simulation state", error=str(e))
                await db.rollback()
    
    async def _initialize_simulation_state(self):
        """Initialize simulation state"""
        await self._save_simulation_state()
        logger.info("Simulation state initialized")
    
    async def _clear_simulation_data(self):
        """Clear simulation data from database"""
        async for db in get_db():
            try:
                # Clear simulation events
                db.query(SimulationEvent).delete()
                
                # Clear simulation states (keep the latest one)
                states = db.query(SimulationState).order_by(SimulationState.created_at.desc()).all()
                if len(states) > 1:
                    for state in states[1:]:
                        db.delete(state)
                
                await db.commit()
                logger.info("Simulation data cleared")
                
            except Exception as e:
                logger.error("Error clearing simulation data", error=str(e))
                await db.rollback() 