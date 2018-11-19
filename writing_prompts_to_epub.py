from ebooklib import epub
import praw

import os
import argparse

from settings import CLIENT_ID, CLIENT_SECRET

parser = argparse.ArgumentParser(description='Generate epub of /r/WritingPrompts.')
parser.add_argument('num_posts', type=int, default=10)
parser.add_argument('num_comments', type=int, default=1)
parser.add_argument('top_criteria', type=str, default="week")
args = parser.parse_args()


reddit = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,user_agent='mozilla')
subreddit = reddit.subreddit('writingprompts')

posts = subreddit.top(time_filter=args.top_criteria, limit=args.num_posts)

book = epub.EpubBook()
book.set_identifier('sample123456')
book.set_title('/r/WritingPrompts')
book.set_language('en')
book.add_author('Reddit')
book.add_metadata('DC', 'description',
                  'An epub generated from the top stories on /r/WritingPrompts')

spine = ['nav']
chapters = []
for pi, post in enumerate(posts):
  storyPromptHtml = "<p><i>%s</i></p><br />" % post.title
  comments = post.comments
  for ci in range(1, args.num_comments+1):
    authorHtml = \
      "<p><strong>This story brought to you by %s</strong></p><br />" \
      % comments[ci].author

    commentText = comments[ci].body
    paragraphs = commentText.split('\n')
    commentHtml = "".join(["<p>%s</p>" % p for p in paragraphs])

    chapterNumber = (pi * args.num_posts) + ci
    chapterTitle = '%s: %s' % (comments[ci].author, post.title)
    chapter = epub.EpubHtml(title='%d: %s' % (chapterNumber, chapterTitle),
                            file_name='ch%d.xhtml' % chapterNumber)
    chapter.set_content(authorHtml + storyPromptHtml + commentHtml)

    book.add_item(chapter)
    chapters.append(chapter)
    spine.append(chapter)

book.spine = spine
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
epub.write_epub('test.epub', book)