"""Capture read-only screenshots from the running Oracle-backed local website.

Requires Playwright with Chromium installed in the invoking Python environment.
The script checks the application's connection status and performs no database writes.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "screenshots"
BASE_URL = "http://127.0.0.1:5001/"


def open_page(page, name: str, selector: str) -> None:
    page.goto(f"{BASE_URL}#{name}", wait_until="domcontentloaded")
    page.locator(selector).first.wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(300)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        response = page.request.get(f"{BASE_URL}api/status")
        status = response.json()
        if not (status.get("success") and status.get("data", {}).get("connected")
                and status["data"].get("demo_mode") is False):
            raise RuntimeError("Oracle is not connected in live mode; screenshots cancelled")

        shots = [
            ("dashboard", ".stat-card"),
            ("books", "#add-book-btn"),
        ]
        for route, selector in shots:
            open_page(page, route, selector)
            assert page.locator("#db-status").inner_text() == "Oracle connected"
            path = OUTPUT / f"{route}.png"
            page.screenshot(path=str(path), full_page=True)
            print(f"Captured {path.relative_to(ROOT)}")

        open_page(page, "members", "#add-member-btn")
        page.locator("#add-member-btn").click()
        path = OUTPUT / "member-registration.png"
        page.locator("#modal-overlay .modal").screenshot(path=str(path))
        print(f"Captured {path.relative_to(ROOT)}")
        page.locator("#modal-overlay .modal-close").click()

        for route in ("issues", "fines"):
            open_page(page, route, "#content table")
            path = OUTPUT / f"{route}.png"
            page.screenshot(path=str(path), full_page=True)
            print(f"Captured {path.relative_to(ROOT)}")

        open_page(page, "reports", '.report-card[data-report="overdue"]')
        page.locator('.report-card[data-report="overdue"]').click()
        page.locator("#export-report-btn").wait_for(state="visible", timeout=15000)
        path = OUTPUT / "overdue-report.png"
        page.screenshot(path=str(path), full_page=False)
        print(f"Captured {path.relative_to(ROOT)}")
        page.locator("#modal-overlay .modal-close").click()

        open_page(page, "databaseLogic", "#run-overdue-demo")
        page.locator("#run-overdue-demo").click()
        page.locator("#overdue-demo-body table").wait_for(state="visible", timeout=15000)
        path = OUTPUT / "overdue-cursor.png"
        page.locator("#overdue-demo-result").screenshot(path=str(path))
        print(f"Captured {path.relative_to(ROOT)}")
        browser.close()


if __name__ == "__main__":
    main()
