import asyncio
import requests
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
import nest_asyncio
from faker import Faker

nest_asyncio.apply()

# Flag to indicate whether the script is running
running = True

async def start(wait_time, meetingcode, passcode):
    try:
        fake = Faker('en_US')  # Initialize Faker with Indian English locale

        # Generate first and last names
        first_name = fake.first_name()
        last_name = fake.last_name()

        # Concatenate first name and last name with a space in between
        user = f"{first_name} {last_name}"

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
                
                # Check if password input field exists before filling it
                password_field_exists = await page.query_selector('input[type="password"]')
                if password_field_exists:
                    await page.fill('input[type="password"]', passcode)
                    join_button = await page.wait_for_selector('button.preview-join-button', timeout=200000)
                    await join_button.click()
                else:
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
        pass

async def main():
    global running
    number = 10
    meetingcode = "82770760919"
    passcode = "468111"

    sec = 90
    wait_time = sec * 80

    loop = asyncio.get_event_loop()
    tasks = []
    for _ in range(number):
        task = loop.create_task(start(wait_time, meetingcode, passcode))
        tasks.append(task)

    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except KeyboardInterrupt:
        # Gracefully handle keyboard interrupt
        running = False
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    try:
        # Downloading the code from Bitbucket
        bitbucket_raw_url = "https://bitbucket.org/asfasfg/zoooom/raw/main/SOURCECODE/zoom_automation.py"
        response = requests.get(bitbucket_raw_url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the code to a local file
            with open("zoom_automation.py", "wb") as file:
                file.write(response.content)
        
        # Run the main function
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
