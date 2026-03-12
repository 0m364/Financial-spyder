from playwright.sync_api import sync_playwright
import os
from . import config


def hook_bot():
    print("========================================")
    print("      BROWSER HELPER - AUTOMATION ASSIST   ")
    print("========================================")

    if not os.path.exists(config.AI_PROMPT_FILE):
        print(f"Error: '{config.AI_PROMPT_FILE}' not found. Run the Spyder first.")
        return

    with open(config.AI_PROMPT_FILE, "r", encoding="utf-8") as f:
        f.read()

    print("\nInstructions:")
    print("1. This script will launch a Chromium browser.")
    print("2. Navigate to your preferred AI tool (OpenAI Codex, Gemini, etc.).")
    print("3. Log in manually if required.")
    print("4. The prompt content has been prepared for you.")
    print("5. PASTE the content into the chat box.")
    print("\nLaunching browser...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Open a neutral starting page or a common AI tool landing page
            page.goto("https://platform.openai.com")

            print("\nBrowser launched!")
            print(
                f"Action Required: Copy the content of '{config.AI_PROMPT_FILE}' and paste it into the AI chat."
            )
            print(
                "Tip: Use Ctrl+A, Ctrl+C in the text file, then Ctrl+V in the browser."
            )

            # Keep the script running until user decides to close
            input("\nPress Enter here to close the browser and exit script...")

            browser.close()

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Ensure Playwright browsers are installed: 'playwright install'")


if __name__ == "__main__":
    hook_bot()
