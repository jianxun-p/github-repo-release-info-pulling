from playwright.sync_api import sync_playwright

from tool import class_tool, function_calling_tool

scroll_amount = 500

@class_tool
class Browser:
    def __init__(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.locators = []
        self.locator = None

    # @function_calling_tool
    def goto(self, url: str):
        """
        Navigate to the specified URL.
        @param url: The URL to navigate to.        
        """
        self.page.goto(url)

    # @function_calling_tool
    def screenshot(self, path="screenshot.png"):
        """
        Take a screenshot of the current page.
        @param path: The file path to save the screenshot. Default is 'screenshot.png'.
        """
        self.page.screenshot(path=path, full_page=False)
        return path

    @function_calling_tool
    def click(self):
        """
        Click at the current locator.
        """
        if self.locator:
            self.locator.click()
            return "Clicked successfully."
        else:
            return "No locator set for clicking."

    @function_calling_tool
    def select_locator(self, index: int):
        """
        Select a locator for subsequent actions.
        @param index: The index of the locator in the list of locators.
        """
        if 0 <= index < len(self.locators):
            self.locator = self.locators[index]
            return str(self.locator.evaluate('el => el.outerHTML'))
        else:
            self.locator = None
            return "Invalid index. No locator selected."

    @function_calling_tool
    def get_by_role(self, role: str, name: str):
        """
        Get a list of elements by the role and name.
        @param role: The role of the element.
        @param name: The name content of the element.
        """
        self.locators = self.page.get_by_role(role, name=name).all()
        return "No locators available" \
            if len(self.locators) == 0 \
            else str([i.evaluate('el => el.outerHTML') for i in self.locators])
    
    @function_calling_tool
    def get_by_text(self, text: str):
        """
        Get a list of elements by the text content.
        @param text: The text content of the element.
        """
        self.locators = self.page.get_by_text(text).all()
        return "No locators available" \
            if len(self.locators) == 0 \
            else str([i.evaluate('el => el.outerHTML') for i in self.locators])

    @function_calling_tool
    def get_by_placeholder(self, text: str):
        """
        Get a list of elements by the placeholder text.
        @param text: The placeholder text of the element.
        """
        self.locators = self.page.get_by_placeholder(text).all()
        return "No locators available" \
            if len(self.locators) == 0 \
            else str([i.evaluate('el => el.outerHTML') for i in self.locators])
    
    @function_calling_tool
    def get_by_title(self, text: str):
        """
        Get a list of elements by the title text.
        @param text: The title text of the element.
        """
        self.locators = self.page.get_by_title(text).all()
        return "No locators available" \
            if len(self.locators) == 0 \
            else str([i.evaluate('el => el.outerHTML') for i in self.locators])
    
    @function_calling_tool
    def get_by_label(self, text: str):
        """
        Get a list of elements by the label text.
        @param text: The label text of the element.
        """
        self.locators = self.page.get_by_label(text).all()
        return "No locators available" \
            if len(self.locators) == 0 \
            else str([i.evaluate('el => el.outerHTML') for i in self.locators])

    @function_calling_tool
    def focus(self):
        """
        Focus on the current locator.
        """
        if self.locator:
            self.locator.focus()
            return "Focused successfully."
        else:
            return "No locator set for focusing"

    @function_calling_tool
    def type(self, text: str):
        """
        Type text using the keyboard. (type "\\n" for enter)
        @param text: The text to type.
        """
        self.page.keyboard.type(text)
        return f'Typed successfully'

    @function_calling_tool
    def scroll(self):
        """
        Scroll vertically.
        """
        global scroll_amount
        self.page.mouse.wheel(0, scroll_amount)
        return f'Scrolled successfully'
    
    @function_calling_tool
    def save_info(self, latest_release: str):
        """
        Save information.
        @param latest_release: The latest release information (JSON string) to save.
        """
        with open("sample_output.json", "w") as f:
            f.write(latest_release)
        self.end = True
        return f'Saved successfully'



