#!/usr/bin/env python3
"""
Modern Website Media Kit Generator
A fast, robust, and self-contained script using Playwright.
"""

import argparse
import asyncio
import json
import os
import shutil
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class MediaKitGenerator:
    def __init__(self, url, delay=1):
        self.url = self._normalize_url(url)
        self.delay = delay
        self.output_dir = "media_kit"
        self.start_time = datetime.now()
        self.playwright = None
        self.browser = None

    async def __aenter__(self):
        """Async context manager to launch the browser."""
        print("🚀 Launching browser via Playwright...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager to close the browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✅ Browser closed.")

    def _normalize_url(self, url):
        """Ensure URL has proper scheme."""
        if not urlparse(url).scheme:
            url = "http://" + url
        return url

    def _create_directories(self):
        """Create output directories."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(os.path.join(self.output_dir, "screenshots"))
        os.makedirs(os.path.join(self.output_dir, "assets"))

    async def take_screenshots(self):
        """Take screenshots for different viewports using Playwright."""
        print("📸 Taking screenshots with Playwright...")
        viewports = {"desktop": (1920, 1080), "tablet": (768, 1024), "mobile": (375, 667)}
        page = await self.browser.new_page()
        try:
            await page.goto(self.url, wait_until='networkidle')
            await page.wait_for_timeout(self.delay * 1000)
            for device, (width, height) in viewports.items():
                print(f"  📱 Capturing {device} view ({width}x{height})...")
                await page.set_viewport_size({"width": width, "height": height})
                screenshot_path = os.path.join(self.output_dir, "screenshots", f"{device}.png")
                await page.screenshot(path=screenshot_path)
                print(f"  ✓ {device} screenshot saved")
        except Exception as e:
            print(f"  ❌ Screenshot error: {e}")
        finally:
            await page.close()

    # <<< THIS IS THE NEW, VASTLY SUPERIOR VIDEO RECORDER >>>
    async def record_scroll_video(self):
        """Record a smooth scroll video using Playwright's built-in recorder."""
        print("📹 Recording scroll video with built-in Playwright recorder...")
        
        # Playwright records to a temporary directory. We'll move it later.
        temp_video_dir = os.path.join(self.output_dir, "temp_video")
        os.makedirs(temp_video_dir)
        
        context = None
        try:
            context = await self.browser.new_context(
                record_video_dir=temp_video_dir,
                record_video_size={"width": 1920, "height": 1080},
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            await page.goto(self.url, wait_until='networkidle')

            # Use JavaScript evaluation to perform a smooth scroll over 10 seconds
            await page.evaluate("""
                async () => {
                    const distance = document.body.scrollHeight - window.innerHeight;
                    const duration = 10000; // 10 seconds
                    let start;
                    await new Promise(resolve => {
                        const step = timestamp => {
                            if (!start) start = timestamp;
                            const progress = timestamp - start;
                            window.scrollTo(0, distance * (progress / duration));
                            if (progress < duration) {
                                window.requestAnimationFrame(step);
                            } else {
                                resolve();
                            }
                        };
                        window.requestAnimationFrame(step);
                    });
                }
            """)
            print("  ✓ Scroll animation complete.")

        except Exception as e:
            print(f"  ❌ An error occurred during video recording: {e}")
        finally:
            if context:
                await context.close() # This saves the video
        
        # Move the recorded video to the final destination
        try:
            video_files = os.listdir(temp_video_dir)
            if video_files:
                temp_video_path = os.path.join(temp_video_dir, video_files[0])
                final_video_path = os.path.join(self.output_dir, "assets", "scroll_demo.mp4")
                shutil.move(temp_video_path, final_video_path)
                print("  ✓ Video saved successfully.")
            shutil.rmtree(temp_video_dir)
        except Exception as e:
            print(f"  ❌ Failed to move video file: {e}")

    # The synchronous methods below remain unchanged
    def get_favicon(self):
        print("🔍 Getting favicon...")
        try:
            response = requests.get(self.url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            selectors = ['link[rel="icon"]', 'link[rel="shortcut icon"]', 'link[rel="apple-touch-icon"]']
            favicon_url = None
            for selector in selectors:
                icon = soup.select_one(selector)
                if icon and icon.get("href"):
                    favicon_url = urljoin(self.url, icon["href"])
                    break
            if not favicon_url: favicon_url = urljoin(self.url, "/favicon.ico")
            favicon_response = requests.get(favicon_url, timeout=10)
            if favicon_response.status_code == 200:
                ext = os.path.splitext(urlparse(favicon_url).path)[1] or ".ico"
                favicon_path = os.path.join(self.output_dir, "assets", f"favicon{ext}")
                with open(favicon_path, "wb") as f: f.write(favicon_response.content)
                print(f"  ✓ Favicon saved as favicon{ext}")
            else:
                print(f"  ❌ Favicon not found (status: {favicon_response.status_code})")
        except Exception as e: print(f"  ❌ Favicon error: {e}")

    def extract_metadata(self):
        print("📊 Extracting metadata...")
        try:
            response = requests.get(self.url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            metadata = {"url": self.url, "timestamp": self.start_time.isoformat(), "title": soup.title.string if soup.title else "No title", "description": "", "keywords": "", "og_title": "", "og_description": "", "og_image": "", "viewport_sizes": {"desktop": "1920x1080", "tablet": "768x1024", "mobile": "375x667"}}
            meta_tags = {"description": soup.find("meta", attrs={"name": "description"}), "keywords": soup.find("meta", attrs={"name": "keywords"}), "og_title": soup.find("meta", attrs={"property": "og:title"}), "og_description": soup.find("meta", attrs={"property": "og:description"}), "og_image": soup.find("meta", attrs={"property": "og:image"})}
            for key, tag in meta_tags.items():
                if tag and (content := tag.get("content")):
                    metadata[key] = urljoin(self.url, content) if key == "og_image" else content
            with open(os.path.join(self.output_dir, "metadata.json"), "w", encoding="utf-8") as f: json.dump(metadata, f, indent=2, ensure_ascii=False)
            print("  ✓ Metadata extracted and saved")
        except Exception as e: print(f"  ❌ Metadata error: {e}")

    def create_readme(self):
        video_line = "- scroll_demo.mp4 - Scrolling demo video" if os.path.exists(os.path.join(self.output_dir, "assets", "scroll_demo.mp4")) else ""
        readme_content = f"""# Website Media Kit ...\n{video_line}\n..."""
        with open(os.path.join(self.output_dir, "README.md"), "w") as f: f.write(readme_content)

    def create_zip(self):
        print("📦 Creating zip archive...")
        zip_name = f"media_kit_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        shutil.make_archive(zip_name, "zip", self.output_dir)
        print(f"  ✓ Archive created: {zip_name}.zip")
        return f"{zip_name}.zip"

    async def generate(self):
        """Generate the complete media kit using async methods."""
        print(f"🚀 Generating media kit for: {self.url}\n" + "-" * 50)
        self._create_directories()
        await self.take_screenshots()
        await self.record_scroll_video()
        self.get_favicon()
        self.extract_metadata()
        self.create_readme()
        zip_file = self.create_zip()
        print("-" * 50 + f"\n✅ Media kit generated successfully!")
        print(f"📁 Folder: {self.output_dir}/")
        print(f"📦 Archive: {zip_file}")
        print(f"⏱️  Total time: {(datetime.now() - self.start_time).total_seconds():.1f}s")


async def main():
    parser = argparse.ArgumentParser(
        description="Generate a modern website media kit using Playwright.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python website_media_kit.py https://example.com
  python website_media_kit.py localhost:3000 --delay 2

Requirements:
  pip install playwright requests beautifulsoup4
  python -m playwright install
        """
    )
    parser.add_argument("url", help="Website URL")
    parser.add_argument("--delay", type=int, default=1, help="Delay in seconds")
    args = parser.parse_args()
    try:
        async with MediaKitGenerator(args.url, args.delay) as generator:
            await generator.generate()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())