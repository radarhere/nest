import wx
import wx.html2

class BrowserWindow(wx.Frame):
	def __init__(self, *args, **kwds):
		wx.Frame.__init__(self, *args, **kwds)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.browser = wx.html2.WebView.New(self)
		sizer.Add(self.browser, 1, wx.EXPAND, 10)
		self.SetSizer(sizer)
		
		menuBar = wx.MenuBar()

		menu = wx.Menu()
		menuItem = menu.Append(wx.ID_ANY, 'Open URL...\tCtrl+O')
		self.SetAcceleratorTable(wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('O'), menuItem.GetId())]))
		self.Bind(wx.EVT_MENU, self.openURL, menuItem)

		self.widescreenMenuItem = menuItem = menu.Append(wx.ID_ANY, 'Switch to widescreen mode\tCtrl+T')
		self.SetAcceleratorTable(wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('T'), menuItem.GetId())]))
		self.Bind(wx.EVT_MENU, self.switchWidescreen, menuItem)
		menuBar.Append(menu, '&File')
		
		self.SetMenuBar(menuBar)
		
		self.widescreen = False
		
		# Initially, wx.Frames are not visible
		self.hidden = True
		
		self.openURL()

	def openURL(self, event = None):
		dialog = wx.TextEntryDialog(self, "Load Page", "Please enter page url")
		if dialog.ShowModal() != wx.ID_OK:
			return
		
		url = dialog.GetValue()
		if not url:
			return
		
		dialog.Destroy()
		
		if not url.startswith('http://') or url.startswith('https://'):
			url = 'http://'+url
		
		self.LoadPage(url)

	def LoadPage(self, url):
		self.browser.LoadURL(url)
		
		if self.hidden:
			self.Show()
			# Alternatively, the window could be shown only on load
			# self.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.Show, self.browser)
			
			self.hidden = False

	def switchWidescreen(self, event):
		self.widescreen = not self.widescreen
		
		if self.widescreen:
			stretchRatio = "0.7"
			# When changing from 4:3 to 16:9, the logical value for this argument would be 0.5625
			# However, experimentally, I have found that 0.7 works. I am unsure about why this discrepancy exists
			
			script = """
				var width = document.getElementsByTagName("body")[0].offsetWidth / """+stretchRatio+""";
				document.getElementsByTagName("body")[0].setAttribute('style','-webkit-transform: scaleX("""+stretchRatio+"""); width: '+width+'px; position: absolute; left: -'+(width * (1 - """+stretchRatio+""") / 2)+'px;');
			"""
		else:
			# If it is changing from widescreen to normal, remove the style argument
			script = """
				document.getElementsByTagName("body")[0].removeAttribute('style');
			"""
		self.browser.RunScript(script)
		
		self.widescreenMenuItem.SetItemLabel('Switch '+('from' if self.widescreen else 'to')+' widescreen mode\tCtrl+T')


def getScreenSize():
	displayNumber = 1 if wx.Display.GetCount() == 2 else 0
	
	display = wx.Display(displayNumber)
	screensize = display.GetGeometry()
	
	if displayNumber == 0:
		# Let's not cover up the main screen completely
		scale = 0.75
		
		screensize.SetWidth(screensize.GetWidth() * scale)
		screensize.SetHeight(screensize.GetHeight() * scale)
		screensize.SetX(screensize.GetX() + screensize.GetWidth() * (1 - scale) / 2)
		screensize.SetY(screensize.GetY() + screensize.GetHeight() * (1 - scale) / 2)
	return screensize

app = wx.App()

dialog = BrowserWindow(None, -1, style=wx.NO_BORDER)
dialog.SetRect(getScreenSize())

app.MainLoop()
