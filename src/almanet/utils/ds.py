class StreamList(list):
	def __init__(self, gen):
		self.gen = gen

	def __iter__(self):
		return self.gen

	def __len__(self):
		return 1