# -*- coding: utf-8 -*-
import re
from alm_crm.models import (
	HashTag, 
	HashTagReference, 
	Mention,
	CRMUser,
	Comment, 
	Activity,
	Share,
	)

def text_parser(base_text, content_class=None, object_id=None):
	hashtag_parser = re.compile(u'\B#\w*[а-яА-ЯёЁa-zA-Z]+\w*', re.U)
	mention_parser = re.compile('\B@\[[0-9]*\:')

	hashtags = hashtag_parser.findall(base_text)
	mentions = mention_parser.findall(base_text)

	# delete hashtags and mention references in case of editing objects
	content_class.objects.get(id=object_id).hashtags.clear()
	content_class.objects.get(id=object_id).mentions.clear()
	
	for hashtag_item in hashtags:
		hashtag, created = HashTag.objects.get_or_create(text=hashtag_item)
		if created:
			hashtag.save()

		if(hashtag):
			hashtag_reference = HashTagReference.build_new(hashtag_id=hashtag.id, 
															content_class=content_class,
															object_id=object_id,
															save=True)

	user_id_parser = re.compile('\d[0-9]*')
	for mention_item in mentions:
		user_id = int(user_id_parser.search(mention_item).group())
		mention = Mention.build_new(user_id=user_id,
									content_class=content_class,
									object_id=object_id,
									save=True)
		