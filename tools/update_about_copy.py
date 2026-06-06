from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
ABOUT = ROOT / "about.html"


REPLACEMENTS = {
    "About Outreach Recruitment | Jobs in Malta": "We Have the Right Profile for You | Outreach Recruitment",
    "Learn how Outreach Recruitment supports EU candidates and employers with jobs in Malta, jobs in Europe, and trusted hiring advice.": "Outreach Recruitment is your trusted recruitment partner, helping employers reach hiring goals with qualified local and international candidates.",
    '<h1 class="heading-h1">About Outreach Recruitment</h1>': '<h1 class="heading-h1">We have the right profile for you</h1>',
    '<div class="button-label" data-figma-id="12018:4671">Watch our story</div>': '<div class="button-label" data-figma-id="12018:4671">Work with us</div>',
    '<div class="tag">At a glance</div><h2 class="heading-h3">From hiring clarity to everyday decision-making, we help growing organizations replace friction with systems that actually hold up over time. No theatrics. Just repeatable structure.</h2>': '<div class="tag">At a glance</div><h2 class="heading-h3">At Outreach Recruitment, we are committed to being your trusted partner in supporting your recruitment needs. We are ready to work with you to help you reach your hiring goals.</h2>',
    'People challenges are rarely caused by lack of effort or ambition. More often, they come from unclear roles, misaligned expectations, and systems that were never designed to handle growth. Our approach focuses on understanding how work actually happens inside organizations and adjusting structures so teams can operate with less confusion, fewer workarounds, and more confidence in everyday decisions.<br/><br/>Our work focuses on reducing friction in how teams hire, collaborate, and make decisions, replacing improvised processes with structures that are clear, repeatable, and practical in day-to-day operations. We help companies move away from reactive fixes and toward systems that continue to function as teams scale, priorities shift, and complexity increases.': 'Finding the right candidate is challenging and time-consuming. We simplify the process by connecting you with experienced talent across various sectors.<br/><br/>Our growing database and global partnerships ensure access to top-quality personnel both locally and internationally.',
    'Built for <em>consistency</em>, not momentum.': 'Connecting <em>talent</em> with opportunity.',
    'We begin by getting how your organization really <em>works</em>': 'We are committed to:',
    'Before proposing solutions, we spend time understanding how decisions are currently made, where responsibility sits, and how information flows across teams. This allows us to identify friction points that slow progress or create unnecessary tension. Our work is grounded in existing realities, ensuring that any changes we design fit naturally into the way teams already operate rather than forcing them into unfamiliar frameworks.': 'Shortlist CVs according to your job description.<br/><br/>Conduct screening interviews and identify the ideal profiles.<br/><br/>Present to you the chosen candidates and coordinate your interview, be it in person or online.<br/><br/>Help you waste less time in your recruitment process.<br/><br/>If the candidate requires a visa, we can take care of it too.<br/><br/>For our commitment, our fees are very favorable when compared to the market.',
    'The team <em>behind </em>success': 'Our mission',
    'Recruitment support for EU candidates and employers': 'Recruitment support built around your hiring goals',
    'Outreach Recruitment understands the Malta job market and European hiring needs. We help candidates find work in Malta and Europe while supporting employers looking for reliable EU talent.': 'We work hand in hand with clients to match profile requirements, support business objectives, and help selected candidates integrate into the working environment.',
}

MISSION_SECTION = '''<section class="section padding-large"><div class="w-layout-blockcontainer container narrow w-container"><div class="w-layout-vflex section-content"><div class="w-layout-vflex section-header"><div class="w-layout-vflex text narrow" data-gsap-scroll="text"><h2 class="heading-h2">Our mission</h2></div></div><div class="w-layout-vflex text narrow" data-gsap-scroll="text"><div class="text-medium">To connect talent with opportunity.<br/><br/>To attract the best talent from our global network and carefully select and recruit quality individuals for our clients in most sectors.<br/><br/>To work hand in hand with our clients in matching their profile requirements and support their business objectives.<br/><br/>To support the integration of selected candidates into the working environment.</div></div></div></div></section>'''


def main() -> None:
    html = ABOUT.read_text()

    for old, new in REPLACEMENTS.items():
        html = html.replace(old, new)

    html, count = re.subn(
        r'<section class="section padding-large"><div class="w-layout-blockcontainer container narrow w-container"><div class="w-layout-vflex section-content"><div class="w-layout-vflex section-header">.*?</section><section class="section outreach-seo"',
        MISSION_SECTION + '<section class="section outreach-seo"',
        html,
        count=1,
        flags=re.S,
    )

    if count != 1:
        raise RuntimeError("Could not replace the About team section")

    ABOUT.write_text(html)
    print("Updated about.html main recruitment copy")


if __name__ == "__main__":
    main()
