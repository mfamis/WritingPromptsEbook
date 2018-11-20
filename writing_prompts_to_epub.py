from ebooklib import epub
import praw

import os
import argparse
import datetime
import logging

from settings import CLIENT_ID, CLIENT_SECRET

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

parser = argparse.ArgumentParser(description='Generate epub of /r/WritingPrompts.')
parser.add_argument('num_posts', type=int, default=10)
parser.add_argument('num_comments', type=int, default=1)
parser.add_argument('top_criteria', type=str, default="week")
args = parser.parse_args()

date = datetime.datetime.now()
date_string = '%d-%d' % (date.month, date.day)

reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent='mozilla')
subreddit = reddit.subreddit('writingprompts')

posts = subreddit.top(time_filter=args.top_criteria, limit=args.num_posts)

# create ebook
book_file_name = 'WP-%s' % date_string
book = epub.EpubBook()
book.set_identifier(book_file_name)
book.set_title('WritingPrompts - Best of %s (%s)' % (args.top_criteria, date_string))
book.set_language('en')
book.add_author('Reddit')
book.add_metadata('DC', 'description',
                  'An epub generated from the top stories on /r/WritingPrompts')

spine = ['nav']
chapters = []
toc = []

# iterate over each post comments to generate chapters
for pi, post in enumerate(posts):
  logging.info('Processing post (%d/%d) titled: %s' % (pi+1, args.num_posts, post.title))
  story_prompt_html = "<p><i>%s</i></p>" % post.title
  comments = post.comments
  for ci in range(1, args.num_comments+1):
    logging.info('Processing comment (%d/%d) titled: %s' \
      % (ci, args.num_comments, comments[ci].author))

    # create a header to credit the comment author
    author_html = \
      "<p><i>(written by %s)</i></p>" \
      % comments[ci].author

    # get the comment data and change it to html
    comment_text = comments[ci].body
    paragraphs = comment_text.split('\n')
    comment_html = "".join(["<p>%s</p>" % p for p in paragraphs])

    # create the epub chapter
    chapter_number = (pi * args.num_comments) + ci
    #chapter_title = '%s: %s' % (comments[ci].author, " ".join(post.title.split(" ")[0:6]))
    chapter_title = '%s: %s' % (comments[ci].author, post.title)
    file_name = 'ch%d.xhtml' % chapter_number
    title = '%d: %s' % (chapter_number, chapter_title)
    chapter = epub.EpubHtml(title=title, file_name=file_name)
    chapter.set_content(story_prompt_html + author_html + comment_html)

    # add the chapter to the book, spine and chapter list
    toc.append(epub.Link(file_name, title, title))
    book.add_item(chapter)
    chapters.append(chapter)
    spine.append(chapter)

logging.info('Finished processing chapters, creating epub: %s' \
  % (book_file_name + ".epub"))
book.toc = toc
book.spine = spine
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())
epub.write_epub(book_file_name + ".epub", book)
logging.info('Done')