import asyncio
import sys
sys.path.insert(0, '.')

# Windows platform special handling
if sys.platform == 'win32':
    from asyncio import WindowsProactorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsProactorEventLoopPolicy())

from app.models.database import AsyncSessionLocal
from app.models.execution import Execution
from app.models.case import TestCase
from app.services.execution_service import execution_service
from sqlalchemy import select

async def test():
    async with AsyncSessionLocal() as db:
        # Get execution 22
        result = await db.execute(select(Execution).where(Execution.id == 22))
        execution = result.scalar_one_or_none()
        
        if execution:
            print(f"Execution ID: {execution.id}")
            print(f"Case IDs JSON: {execution.case_ids_json}")
            print(f"Case IDs List: {execution.case_ids_list}")
            
            case_ids = execution.case_ids_list
            if case_ids:
                case_query = select(TestCase).where(TestCase.id.in_(case_ids))
                case_result = await db.execute(case_query)
                cases = case_result.scalars().all()
                print(f"Found {len(cases)} cases")
                for case in cases:
                    print(f"  - Case {case.id}: {case.name}")
            else:
                print("No case IDs found!")

asyncio.run(test())
