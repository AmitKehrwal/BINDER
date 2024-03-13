import asyncio
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
import nest_asyncio
from faker import Faker

nest_asyncio.apply()

# Flag to indicate whether the script is running
running = True

async def start(wait_time, meetingcode):
    try:
        faker = Faker()

        user = faker.name()  # Generate a random name using faker

        print(f"{user} joined.")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            context = await browser.new_context()

            page = await context.new_page()
            await page.goto(f'http://app.zoom.us/wc/join/{meetingcode}', timeout=200000)

            # Explicitly request microphone permission using JavaScript multiple times
            for _ in range(5):
                await page.evaluate('() => { navigator.mediaDevices.getUserMedia({ audio: true }); }')

            try:
                await page.click('//button[@id="onetrust-accept-btn-handler"]', timeout=5000)
            except Exception as e:
                pass

            try:
                await page.click('//button[@id="wc_agree1"]', timeout=5000)
            except Exception as e:
                pass

            try:
                await page.wait_for_selector('input[type="text"]', timeout=200000)
                await page.fill('input[type="text"]', user)
                # No need to fill passcode
                join_button = await page.wait_for_selector('button.preview-join-button', timeout=200000)
                await join_button.click()
            except Exception as e:
                pass

            try:
                await page.wait_for_selector('button.join-audio-by-voip__join-btn', timeout=300000)
                query = 'button[class*="join-audio-by-voip__join-btn"]'
                mic_button_locator = await page.query_selector(query)
                await asyncio.sleep(5)
                await mic_button_locator.evaluate_handle('node => node.click()')
                print(f"{user} mic aayenge.")
            except Exception as e:
                print(f"{user} mic nahe aayenge. ", e)

            print(f"{user} sleep for {wait_time} seconds ...")
            while running and wait_time > 0:
                await asyncio.sleep(1)
                wait_time -= 1
            print(f"{user} ended!")

        # Close the context and browser outside of the async with block
        await context.close()
        await browser.close()

    except Exception as e:
        print(f"An error occurred: {e}")
