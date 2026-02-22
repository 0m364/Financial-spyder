from playwright.sync_api import sync_playwright
import os

def hook_bot():
    print("========================================")
    print("      AI BOT HOOK - AUTOMATION ASSIST   ")
    print("========================================")

    if not os.path.exists("ai_briefing.txt"):
        print("Error: 'ai_briefing.txt' not found. Run Corporate_SPYder.py first.")
        return

    with open("ai_briefing.txt", "r", encoding="utf-8") as f:
        prompt_content = f.read()

    print("\nInstructions:")
    print("1. This script will launch a Chromium browser.")
    print("2. Navigate to your preferred AI tool (ChatGPT, Gemini, etc.).")
    print("3. Log in manually if required.")
    print("4. The prompt content has been prepared for you.")
    print("5. PASTE the content into the chat box.")
    print("\nLaunching browser...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Open a neutral starting page or a common AI tool landing page
            page.goto("https://chat.openai.com")

            print("\nBrowser launched!")
            print("Action Required: Copy the content of 'ai_briefing.txt' and paste it into the AI chat.")
            print("Tip: Use Ctrl+A, Ctrl+C in the text file, then Ctrl+V in the browser.")

            # Keep the script running until user decides to close
            input("\nPress Enter here to close the browser and exit script...")

            browser.close()

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Ensure Playwright browsers are installed: 'playwright install'")

if __name__ == "__main__":
    hook_bot()
