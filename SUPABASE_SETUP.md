# Supabase Setup Guide for NeuraRoute

## Backend Configuration

### 1. Environment Variables
Add the following to your backend `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

### 2. Install Dependencies
The Supabase Python client has been added to `requirements.txt`. Install it:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Usage in Backend
The backend now includes:
- `app/core/supabase.py` - Supabase client configuration
- `app/services/supabase_service.py` - Service layer for database operations

Example usage:
```python
from app.services.supabase_service import get_supabase_service

# Get service instance
service = get_supabase_service()

# Fetch all fleet records
fleet_data = await service.get_all("fleet")

# Create a new record
new_fleet = await service.create("fleet", {
    "vehicle_id": "V001",
    "vehicle_type": "truck",
    "capacity": 1000,
    "current_location": "Warehouse A",
    "status": "available"
})
```

## Frontend Configuration

### 1. Environment Variables
Create a `.env` file in the frontend directory:

```bash
# Supabase Configuration
REACT_APP_SUPABASE_URL=your_supabase_project_url_here
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Map Configuration
REACT_APP_MAPBOX_TOKEN=your_mapbox_token_here
```

### 2. Install Dependencies
The Supabase JavaScript client has been added to `package.json`. Install it:

```bash
cd frontend
npm install
```

### 3. Usage in Frontend
The frontend now includes:
- `src/services/supabaseClient.ts` - Supabase client configuration
- `src/services/supabaseService.ts` - Service layer for database operations

Example usage:
```typescript
import { supabaseService } from './services/supabaseService'

// Fetch all fleet records
const fleet = await supabaseService.getFleet()

// Create a new fleet record
const newFleet = await supabaseService.createFleet({
  vehicle_id: "V001",
  vehicle_type: "truck",
  capacity: 1000,
  current_location: "Warehouse A",
  status: "available"
})
```

## Database Schema

The following tables are expected in your Supabase database:

### Fleet Table
```sql
CREATE TABLE fleet (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id TEXT NOT NULL,
  vehicle_type TEXT NOT NULL,
  capacity INTEGER NOT NULL,
  current_location TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Merchants Table
```sql
CREATE TABLE merchants (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  location TEXT NOT NULL,
  contact_info TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Inventory Table
```sql
CREATE TABLE inventory (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  item_name TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  location TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Orders Table
```sql
CREATE TABLE orders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  merchant_id UUID REFERENCES merchants(id),
  items TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Getting Your Supabase Credentials

1. Go to [Supabase](https://supabase.com/) and create a new project
2. Once your project is ready, go to **Project Settings > API**
3. Copy your **Project URL** and **anon/public key**
4. For backend operations, also copy your **service_role key** (keep this secure)

## Migration from Existing Database

If you have existing data in your PostgreSQL database:

1. Export your data from the existing database
2. Import the data into your Supabase database using the SQL editor
3. Update your application to use the new Supabase endpoints

## Testing the Setup

### Backend Test
```bash
cd backend
python -c "
from app.core.supabase import is_supabase_configured
print('Supabase configured:', is_supabase_configured())
"
```

### Frontend Test
```bash
cd frontend
npm start
```

Then check the browser console for any Supabase connection errors.

## Security Notes

- Never expose your `SUPABASE_SERVICE_ROLE_KEY` in the frontend
- Use Row Level Security (RLS) policies in Supabase for data protection
- The anon key is safe to use in the frontend as it respects RLS policies 