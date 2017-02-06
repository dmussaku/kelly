# -*- coding: utf-8 -*-
import re
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from alm_crm.models import (
    HashTag, 
    HashTagReference, 
    Mention,
    Comment, 
    Activity,
    Share,
    )

MENTION_PARSER = re.compile('\B@\[[0-9]*\:')
HASHTAG_PARSER = re.compile(u'\B#\w*[а-яА-ЯёЁa-zA-Z]+\w*', re.U)


def text_parser(base_text, company_id, content_class=None, object_id=None):
    if base_text == None or base_text == "":
        return
        
    content_type =  ContentType.objects.get_for_model(content_class)

    hashtags = HASHTAG_PARSER.findall(base_text)
    mentions = MENTION_PARSER.findall(base_text)

    # delete hashtags and mention references in case of editing objects
    # content_class.objects.get(id=object_id).hashtags.clear()
    content_class.objects.get(id=object_id).mentions.clear()    

    # delete hashtags that not included in new text
    already_added_hastags = HashTagReference.objects.filter(content_type=content_type, object_id=object_id)
    for hashtagRef in already_added_hastags:
        if not hashtagRef.hashtag.text in hashtags:
            _h = hashtagRef.hashtag
            hashtagRef.delete()
            if len(_h.references.all()) == 0:
                _h.delete()


    for hashtag_item in hashtags:
        hashtag, created = HashTag.objects.get_or_create(text=hashtag_item, company_id=company_id)
        if created:
            hashtag.save()

        if(hashtag):
            # check for prevent adding already added reference
            newRef = content_type.__str__()+str(object_id)
            refs = [r.content_type.__str__()+str(r.object_id) for r in hashtag.references.all()]

            if not newRef in refs:
                hashtag_reference = HashTagReference.build_new(
                    hashtag_id=hashtag.id, 
                    content_class=content_class,
                    object_id=object_id,
                    company_id = company_id,
                    save=True)


    user_id_parser = re.compile('\d[0-9]*')
    for mention_item in mentions:
        user_id = int(user_id_parser.search(mention_item).group())
        mention = Mention.build_new(user_id=user_id,
                                    content_class=content_class,
                                    object_id=object_id,
                                    company_id = company_id,
                                    save=True)
        