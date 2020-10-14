import requests
import bs4
import urllib
import time


# 提取准确的结果
class Get_Precise_Results():
	# 初始化
	def __init__(self, key_word, page_num=10):
		self.key_word = key_word
		self.page_num = page_num
		self.headers = {
			'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.32 Safari/537.36'
			}
	# 外部运行
	def run(self):
		results_dic = {}
		for i in range(self.page_num):
			temp1 = self._get_one_page_result(i)
			temp2 = self._analysis_links_temp(temp1)
			results_dic[i] =  temp2
		return results_dic
	# 获取一页的有效链接
	def _get_one_page_result(self, page):
		print('[INFO]:Getting Page %s...' % page)
		links_temp = set()
		self.query_url = 'https://www.baidu.com/s?wd={}&pn={}'.format(urllib.parse.quote(self.key_word), page*10)
		res = requests.get(self.query_url, headers=self.headers)
		html_content = res.content
		soup = bs4.BeautifulSoup(html_content, 'lxml')
		left_content = soup.find('div', attrs={'id': 'content_left'})
		result_url_list = left_content.find_all('a')
		for result_url in result_url_list:
			link = result_url.get('href')
			try:
				if link.find('http://www.baidu.com/link?url=') != -1:
					links_temp.add(link)
			except:
				continue
		return links_temp
	# 获得跳转之后的结果
	def _analysis_links_temp(self, links_temp):
		print('[INFO]:Start analysis...')
		result_links = set()
		for link in links_temp:
			try:
				res = requests.get(link, headers=self.headers)
			except:
				print('[ERROR]:Link %s analysis failure...' % link)
				continue
			url = res.url
			result_links.add(url)
		results = []
		for rl in result_links:
			title = self._get_url_title(rl)
			if title:
				results.append([title, rl])
			else:
				results.append(['无标题', rl])
		return results
	# 获得跳转结果的网页标题
	def _get_url_title(self, url):
		print('[INFO]:Getting title...')
		res = requests.get(url, headers=self.headers)
		soup = bs4.BeautifulSoup(res.text, 'lxml')
		try:
			url_title = soup.find('title').string.strip()
		except:
			url_title = None
		return url_title



# 内部调试
if __name__ == '__main__':
	while True:
		key_word = input('Enter the key word:')
		page_num = input('Enter the results pages:')
		try:
			page_num = int(page_num)
		except:
			print('pages should be digital...')
			continue
		if page_num < 1:
			print('Page number need >0...')
			continue
		results = Get_Precise_Results(key_word, page_num).run()
		print('[INFO]:Start to save data...')
		f = open('results.txt', 'w', encoding='utf-8')
		f.truncate()
		f.close()
		f = open('results.txt', 'a', encoding='utf-8')
		for i in range(page_num):
			f.write('Page%s:\n' % i)
			contents = results[i]
			for c in contents:
				f.write(str(c[0])+':'+str(c[1])+'\n')
		f.close()
		print('All things Done...')
