import re
from alm_crm import (
	HashTag, 
	HashTagReference, 
	Mention,
	CRMUser,
	Comment, 
	Activity,
	Share,
	)

def text_parser(base_text):
	hashtag_parser = re.compile('\B#\w*[a-zA-Z]+\w*') 
	mention_parser = re.compile('\B@\[[0-9]*\:')

	hashtags = hashtag_parser.findall(base_text)
	mentions = mention_parser.findall(base_text)

	for hashtag_item in hashtags:
		hashtag = HashTag.objects.get_or_create(hashtag_item)