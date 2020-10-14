# 酷狗音乐下载器
# 作者：Charles
# 公众号：Charles的皮卡丘
import requests
import re
import os


class Downloader():
	def __init__(self):
		self.headers = {
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
					}
		self.search_url = 'http://songsearch.kugou.com/song_search_v2?keyword={}&page=1&pagesize=30'
		self.hash_url = 'http://www.kugou.com/yy/index.php?r=play/getdata&hash={}'
	def run(self, keyword, num=1):
		res = requests.get(self.search_url.format(keyword), headers=self.headers)
		filehash = re.findall('"FileHash":"(.*?)"', res.text)
		songname = re.findall('"SongName":"(.*?)"', res.text)
		if num > len(filehash):
			print('[Warning]:Only find %d songs...' % len(filehash))
			num = len(filehash)
		names = []
		if not os.path.exists('./results'):
				os.mkdir('./results')
		for n in range(num):
			content = requests.get(self.hash_url.format(filehash[n]))
			name = songname[n].replace("<\\/em>", "").replace("<em>", "") + '.mp3'
			if name in names:
				name = str(n) + name
			names.append(name)
			url = re.findall('"play_url":"(.*?)"', content.text)[0]
			download_url = url.replace("\\", "")
			print('[INFO]:Downloading %dth song...' % (n+1))
			with open('./results/{}'.format(name), 'wb') as f:
				f.write(requests.get(download_url).content)
		print('[INFO]:All done...')



if __name__ == '__main__':
	while True:
		print('[INFO]:Kougou music Downloader...')
		print('[Author]:Charles')
		keyword = input('Enter the SongName:')
		songnum = input('Enter the num you want to download(Max:30):')
		try:
			songnum = int(songnum)
		except:
			continue
		dl = Downloader()
		dl.run(keyword, songnum)