import asyncio
import sys

# Windows platform special handling
if sys.platform == 'win32':
    try:
        from asyncio import WindowsProactorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsProactorEventLoopPolicy())
        print("[OK] Set WindowsProactorEventLoopPolicy")
    except ImportError:
        print("[ERROR] Cannot import WindowsProactorEventLoopPolicy")

from app.engines.playwright_engine import PlaywrightEngine

async def main():
    print("Starting Playwright engine test...")
    engine = PlaywrightEngine(browser_type="chromium", headless=True)
    
    try:
        print("Starting browser...")
        await engine.start_browser()
        print("[OK] Browser started successfully!")
        
        print("Navigating to Baidu...")
        result = await engine.execute_navigate("https://www.baidu.com")
        print(f"Navigate result: {result}")
        
        await asyncio.sleep(2)
        print("Test completed!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Closing browser...")
        await engine.close_browser()
        print("[OK] Browser closed")

if __name__ == "__main__":
    asyncio.run(main())
