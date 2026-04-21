#!/usr/bin/env python3
"""
Daily Architecture Challenge Generator
Generates an HTML blog post and updates the challenge index page.
Designed to run inside a Claude Code Routine.

Usage:
  python3 generate_post.py --title "Rate Limiting in Multi-Tenant APIs" \
    --category "Scalability" --number 1 \
    --problem "How would you design..." \
    --solution "<p>The key approach...</p>" \
    --when-to-use "High-traffic APIs|Multi-tenant SaaS|Rate-sensitive endpoints" \
    --when-to-avoid "Internal-only APIs|Low-traffic services|Real-time streaming" \
    --pattern-name "Token Bucket" \
    --pattern-desc "A token bucket algorithm..." \
    --deeper-link "https://blog.example.com/rate-limiting" \
    --deeper-text "How Stripe Built Their Rate Limiter" \
    --subtitle "A practical approach to fair resource allocation across tenants"
"""

import argparse
import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_DIR = os.path.join(SCRIPT_DIR, '..', 'blog', 'architecture-challenge')
TEMPLATE_PATH = os.path.join(BLOG_DIR, 'template.html')
INDEX_PATH = os.path.join(BLOG_DIR, 'index.html')


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def generate_post(args):
    """Generate a blog post HTML file from the template."""
    with open(TEMPLATE_PATH, 'r') as f:
        template = f.read()

    today = datetime.now()
    date_display = today.strftime('%B %d, %Y')
    date_slug = today.strftime('%Y-%m-%d')
    filename_slug = f"{date_slug}-{slugify(args.title)}"

    # Build problem HTML
    problem_paragraphs = args.problem.split('|')
    problem_html = '\n'.join(f'    <p>{p.strip()}</p>' for p in problem_paragraphs)

    # Build when-to-use / when-to-avoid lists
    use_items = args.when_to_use.split('|')
    avoid_items = args.when_to_avoid.split('|')
    use_html = '\n'.join(f'            <li>{item.strip()}</li>' for item in use_items)
    avoid_html = '\n'.join(f'            <li>{item.strip()}</li>' for item in avoid_items)

    # Meta description
    meta_desc = args.subtitle if args.subtitle else args.problem[:160]

    # Replace all placeholders
    replacements = {
        '{{TITLE}}': args.title,
        '{{SUBTITLE}}': args.subtitle or '',
        '{{META_DESCRIPTION}}': meta_desc,
        '{{DATE_DISPLAY}}': date_display,
        '{{CATEGORY}}': args.category,
        '{{CHALLENGE_NUMBER}}': str(args.number),
        '{{FILENAME}}': filename_slug + '.html',
        '{{PROBLEM_HTML}}': problem_html,
        '{{SOLUTION_HTML}}': args.solution,
        '{{WHEN_TO_USE_HTML}}': use_html,
        '{{WHEN_TO_AVOID_HTML}}': avoid_html,
        '{{PATTERN_NAME}}': args.pattern_name,
        '{{PATTERN_DESCRIPTION}}': args.pattern_desc,
        '{{DEEPER_LINK}}': args.deeper_link,
        '{{DEEPER_LINK_TEXT}}': args.deeper_text,
    }

    html = template
    for key, value in replacements.items():
        html = html.replace(key, value)

    # Write the post file
    post_path = os.path.join(BLOG_DIR, f'{filename_slug}.html')
    with open(post_path, 'w') as f:
        f.write(html)

    print(f"✅ Post created: {post_path}")

    # Update the index page
    update_index(args, filename_slug, date_display)

    return post_path


def update_index(args, filename_slug, date_display):
    """Add new challenge card to the index page."""
    with open(INDEX_PATH, 'r') as f:
        index_html = f.read()

    # Build the new card HTML
    new_card = f'''    <a href="/blog/architecture-challenge/{filename_slug}.html" class="challenge-card" data-category="{args.category.lower()}">
      <span class="challenge-number">#{args.number:03d}</span>
      <div class="challenge-content">
        <h3>{args.title}</h3>
        <p>{args.subtitle or ''}</p>
        <div class="challenge-tags">
          <span class="challenge-tag">{args.category}</span>
          <span class="challenge-tag">{args.pattern_name}</span>
        </div>
      </div>
      <span class="challenge-date">{date_display}</span>
    </a>'''

    # Insert after the placeholder comment (newest first)
    placeholder = '<!-- CHALLENGES_PLACEHOLDER -->'
    if placeholder in index_html:
        index_html = index_html.replace(
            placeholder,
            f'{placeholder}\n{new_card}'
        )
    else:
        # If no placeholder, insert before closing </div> of challenge-list
        index_html = index_html.replace(
            '</div>\n</div>\n\n<footer>',
            f'{new_card}\n  </div>\n</div>\n\n<footer>'
        )

    with open(INDEX_PATH, 'w') as f:
        f.write(index_html)

    print(f"✅ Index updated with challenge #{args.number}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate architecture challenge blog post')
    parser.add_argument('--title', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--number', type=int, required=True)
    parser.add_argument('--problem', required=True, help='Problem text, use | for paragraph breaks')
    parser.add_argument('--solution', required=True, help='Solution HTML')
    parser.add_argument('--when-to-use', required=True, help='Pipe-separated list')
    parser.add_argument('--when-to-avoid', required=True, help='Pipe-separated list')
    parser.add_argument('--pattern-name', required=True)
    parser.add_argument('--pattern-desc', required=True)
    parser.add_argument('--deeper-link', required=True)
    parser.add_argument('--deeper-text', required=True)
    parser.add_argument('--subtitle', default='')

    args = parser.parse_args()
    generate_post(args)
