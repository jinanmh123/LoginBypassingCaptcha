import asyncio
import logging
import capsolver
from pyppeteer import launch
from pyppeteer_stealth import stealth
import datetime

# Consider using environment variables for sensitive information
capsolver.api_key = input("Enter your capsolver api key: ")
PROXY = "http://username:password@host:port"

async def solve_recaptcha_v2(url, key):
    solution = capsolver.solve({
        "type": "ReCaptchaV2Task",
        "websiteURL": url,
        "websiteKey": key, # the captcha v2 public domain key (can be found in the website)
        "proxy": PROXY
    })
    return solution['gRecaptchaResponse']

async def solve_recaptcha_v3(url, key, page_action):
    solution = capsolver.solve({
        "type": "ReCaptchaV3M1TaskProxyLess",
        "websiteURL": url,
        "websiteKey": key, # the recaptcha v3 public domain key (can be found in the website)
        "pageAction": page_action
    })
    return solution["gRecaptchaResponse"]

async def login_with_recaptcha():
    site_ad = "https://visa.vfsglobal.com/lka/en/ita/application-detail"
    email = "mailex@gmail.com"
    password = "passex@"

    try:
        browser = await launch({"headless": False, "userDataDir": "./tool/pyppeteer", "autoClose": False,
                                "args": ["--no-sandbox", "--start-maximized", "--disable-infobars",
                                         "--disable-dev-shm-usage"]})

        page = await browser.newPage()
        await stealth(page)
        await page.setViewport({"width": 924, "height": 668})
        page.setDefaultNavigationTimeout(0)
        await page.goto(site_ad, {'timeout': 60000})

        await page.waitForSelector('#mat-input-0')
        await page.type('#mat-input-0', str(email))
        await page.waitForSelector('#mat-input-1')
        await page.type('#mat-input-1', str(password))

        # Solve reCAPTCHA V2
        solution_v2 = await solve_recaptcha_v2(site_ad, "YourV2SiteKey")

        # Inject the solution into the page for reCAPTCHA V2
        await page.evaluate(
            """(responsetext) => {
               const responseInput = document.querySelector('textarea[id="g-recaptcha-response"]');
               responseInput.value = responsetext;
            }""", solution_v2
        )

        # Solve reCAPTCHA V3
        solution_v3 = await solve_recaptcha_v3(site_ad, "YourV3SiteKey", "login_action")

        # Inject the solution into the page for reCAPTCHA V3
        await page.evaluate(
            """(responsetext) => {
               const responseInput = document.querySelector('textarea[id="g-recaptcha-response-100000"]');
               responseInput.value = responsetext;
            }""", solution_v3
        )

        # Continue with the login process...

        await page.waitFor(3000)
        await page.close()
        await browser.close()
        logging.info("End work with browser at {0}".format(datetime.datetime.now()))

    except Exception as e:
        logging.error("Error: ", exc_info=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(login_with_recaptcha())
    loop.close()
