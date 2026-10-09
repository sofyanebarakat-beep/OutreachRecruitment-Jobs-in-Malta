"""Build the customer service blog cluster that supports /customer-service-jobs-in-malta.

Creates blog/<slug>.html for each post in POSTS (cloned from the construction salary
post template), crops featured images from the hub photos, adds cards to blog/index.html
and entries to sitemaps/sitemap-blog.xml + sitemap-blog-images.xml.
Idempotent: re-running rewrites the posts and skips cards/sitemap entries that exist.

    python3 tools/build_customer_service_blog.py
"""
import json, re, sys, html as H
from pathlib import Path
from PIL import Image

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "blog" / "construction-worker-salary-malta.html"
BASE = "https://outreachrecruitment.net"
HUB = "/customer-service-jobs-in-malta"
DATE = "2026-10-09"
DATE_EN = "October 9, 2026"

# Featured images are landscape crops of the two hub photos (1800x2400).
W_IMG = ROOT / "assets" / "customer-service-malta-call-centre-hero.webp"   # woman, Valletta view
M_IMG = ROOT / "assets" / "jobs-malta-customer-support.webp"               # man with headset


def faq_html(faqs, tpl_item):
    return ('<section class="article-faq-section"><h2>{h}</h2><div class="faq-list" data-gsap-scroll="stagger">'
            + "".join(tpl_item.replace("@@Q@@", q).replace("@@A@@", a) for q, a in faqs[1]) + "</div></section>").format(h=faqs[0])


POSTS = []

# ------------------------------------------------------------------ 1. salaries
POSTS.append(dict(
    slug="call-centre-salary-malta", lang="en", sub="career-planning",
    img=(W_IMG, (0, 560, 1800, 1572)),
    title="Call Centre Salary in Malta 2026: What Customer Service Jobs Pay",
    h1="Call centre salary in Malta 2026",
    desc="What do call centre and customer service jobs in Malta pay? Real published salaries, what raises pay (languages, shifts, bonuses) and gross vs net.",
    alt="Call centre agent with headset in a Malta office overlooking Valletta — call centre salary in Malta",
    keywords="call centre salary Malta, customer service salary Malta, call agent salary Malta, contact centre pay Malta",
    tag="Jobs in Malta", read=6,
    body=f"""<section><div class="answer-box"><strong>Quick answer:</strong> In the customer service roles we recruit for in Malta, the Customer Contact Agent position pays <strong>&euro;19,000 &ndash; &euro;22,000 per year</strong> (about &euro;1,580 &ndash; &euro;1,830 gross per month), and a recent assistance co-ordinator role advertised &euro;23,000 &ndash; &euro;27,000. Languages, shift work and bonuses are what push pay higher. See every open role on our <a href="{HUB}">customer service jobs in Malta</a> page.</div></section>
<section><h2>Key Takeaways</h2><ul>
<li>Entry and mid-level call centre salaries in our listings sit around &euro;19,000 &ndash; &euro;22,000 a year.</li>
<li>Co-ordinator and team-lead roles pay more, with recent adverts in the &euro;23,000 &ndash; &euro;27,000 range.</li>
<li>A second language such as French, Italian, Arabic or Maltese is the single biggest lever on your pay and options.</li>
<li>24/7 rotas often add a shift allowance on top of base salary.</li>
<li>Salaries are quoted gross &mdash; always estimate your net pay before comparing offers.</li></ul></section>
<section><h2>Call centre salaries in Malta: real figures from our listings</h2>
<p>Salary surveys often quote averages that no employer actually offers. The figures below are taken from customer service and contact centre jobs we have advertised for our clients, exactly as the employers published them:</p>
<div class="article-table-wrap"><table class="check-table"><thead><tr><th>Role</th><th>Location</th><th>Published pay</th><th>Status</th></tr></thead><tbody>
<tr><td><a href="/jobs/customer-contact-agent/">Customer Contact Agent</a></td><td>Floriana</td><td>&euro;19,000 &ndash; &euro;22,000 per year</td><td>Hiring now</td></tr>
<tr><td><a href="/jobs/assistance-operations-coordinator/">Assistance Operations Coordinator</a></td><td>Floriana</td><td>Base salary + shift allowance &amp; performance bonus</td><td>Hiring now</td></tr>
<tr><td><a href="/jobs/customer-contact-centre-representative/">Customer Contact Centre Representative (Maltese speaking)</a></td><td>Floriana</td><td>Negotiable</td><td>Hiring now</td></tr>
<tr><td>Assistance Co-ordinator</td><td>Floriana</td><td>&euro;23,000 &ndash; &euro;27,000 per year</td><td>Recently filled</td></tr>
<tr><td>Airline Sales, Reservations &amp; Ticketing Officer</td><td>Luqa</td><td>&euro;20,500 &ndash; &euro;21,000 per year</td><td>Recently filled</td></tr>
</tbody></table></div>
<p>&ldquo;Negotiable&rdquo; means the employer sets the figure after interview, based on your experience and languages. Our consultants share the expected range with shortlisted candidates before the interview, so you never go in blind.</p></section>
<section><h2>What affects a call centre salary in Malta?</h2>
<ul>
<li><strong>Languages.</strong> Fluent English is required everywhere. Adding French, Italian, German, Arabic or Maltese qualifies you for language desks that are harder to fill &mdash; and therefore better paid and easier to get into. Our guide to <a href="/blog/language-requirements-customer-service-jobs-malta">language requirements for customer service jobs</a> explains what &ldquo;fluent&rdquo; means in practice.</li>
<li><strong>Shift pattern.</strong> Roles covering nights, weekends and public holidays, such as 24/7 assistance desks, often pay a shift allowance on top of base salary.</li>
<li><strong>Industry.</strong> Insurance, travel assistance and financial services desks tend to pay more than general inbound support because agents handle policies, claims and sensitive data.</li>
<li><strong>Responsibility.</strong> Moving from agent to co-ordinator, quality analyst or team leader is the usual route to a higher salary band.</li>
<li><strong>Sales targets.</strong> Some contact centre roles, like the Maltese-speaking representative position, include a production or sales bonus.</li></ul></section>
<div class="cta-box"><h2>See call centre jobs hiring now</h2><p>Every open customer service, call centre and call agent job in Malta, with salaries shown where published.</p><a href="{HUB}">Browse call centre jobs in Malta</a></div>
<section><h2>Monthly and hourly equivalents</h2>
<p>To compare offers quoted in different ways, divide the yearly figure by 12 for a monthly gross amount, or by about 2,080 (52 weeks &times; 40 hours) for an hourly rate. A &euro;19,000 salary is roughly &euro;1,583 a month or &euro;9.13 an hour gross; &euro;22,000 is roughly &euro;1,833 a month or &euro;10.58 an hour.</p></section>
<section><h2>Gross versus net pay</h2>
<p>Advertised salaries in Malta are quoted before income tax and social security contributions, so your take-home pay will be lower. Full-time employees also receive statutory bonuses during the year, paid leave and sick leave, which are not always included in the headline figure. Use our <a href="/salary-calculator-malta">Malta salary calculator</a> to estimate your net monthly pay.</p></section>
<section><h2>How to earn more in customer service in Malta</h2>
<ul>
<li>Lead with your languages on your CV and say clearly which ones you can work in on the phone.</li>
<li>Be open to rotating or 24/7 shifts if the allowance matters to you.</li>
<li>Aim for co-ordinator, quality or team-lead roles after 12&ndash;18 months of solid KPIs.</li>
<li>Prepare well for interviews &mdash; see our list of <a href="/blog/call-centre-interview-questions-malta">call centre interview questions in Malta</a> with sample answers.</li></ul></section>""",
    faqs=("FAQs", [
        ("How much does a call centre agent earn in Malta?",
         "In our current listings, the Customer Contact Agent role pays &euro;19,000 &ndash; &euro;22,000 per year gross. Co-ordinator roles have recently been advertised at &euro;23,000 &ndash; &euro;27,000 per year."),
        ("Do multilingual call centre agents earn more in Malta?",
         "Usually yes. A second working language such as French, Italian, Arabic or Maltese qualifies you for language desks that are harder to fill, which tends to mean better pay and more job options."),
        ("Is call centre pay in Malta quoted gross or net?",
         "Gross. Income tax and social security are deducted from the advertised figure, so take-home pay is lower. Use a Malta salary calculator to estimate your net pay."),
        ("Where can I find call centre jobs in Malta with published salaries?",
         "Our customer service jobs in Malta page lists every open call centre and call agent vacancy we recruit for, with the salary wherever the employer has published it."),
    ]),
    cta=("Find your next call centre job", "Browse open customer service and call agent jobs in Malta, with salaries shown where published.", "View customer service jobs in Malta"),
    related=["language-requirements-customer-service-jobs-malta", "call-centre-interview-questions-malta", "emploi-centre-appels-malte-francophones"],
))

# ------------------------------------------------------------------ 2. French guide
POSTS.append(dict(
    slug="emploi-centre-appels-malte-francophones", lang="fr", sub="career-planning",
    img=(W_IMG, (540, 300, 1800, 1009)),
    title="Travailler dans un centre d'appels à Malte : guide pour francophones",
    h1="Travailler dans un centre d'appels à Malte : le guide pour les francophones",
    desc="Emploi en service client et centre d'appels à Malte pour francophones : postes ouverts, salaire de 19 000 à 22 000 €, langues, horaires et candidature.",
    alt="Conseillère service client avec casque dans un centre d'appels à Malte, vue sur La Valette",
    keywords="emploi centre d'appels Malte, service client Malte, travailler à Malte francophone, emploi Malte français",
    tag="Emploi à Malte", read=6,
    body=f"""<section><div class="answer-box"><strong>En bref :</strong> Malte recrute en permanence des conseillers service client francophones. Le poste de <strong>Customer Contact Agent</strong> à Floriana, que nous recrutons actuellement, demande un anglais courant et le français (seul ou avec l'arabe), avec un salaire de <strong>19 000 &ndash; 22 000 &euro; par an</strong>. Voir toutes les offres sur notre page <a href="{HUB}">emplois service client à Malte</a>.</div></section>
<section><h2>Points clés</h2><ul>
<li>L'anglais courant est obligatoire pour tous les postes ; le français est votre principal atout.</li>
<li>Combinaisons recherchées : anglais + français, ou anglais + arabe + français.</li>
<li>Salaire publié : 19 000 &ndash; 22 000 &euro; brut par an, soit environ 1 580 &ndash; 1 830 &euro; brut par mois.</li>
<li>Semaine de 40 heures en rotation, y compris week-ends et jours fériés.</li>
<li>La candidature se fait en ligne ; notre équipe vous rappelle pour un premier entretien téléphonique.</li></ul></section>
<section><h2>Pourquoi Malte recrute des francophones</h2>
<p>Malte est l'un des grands centres européens du service client multilingue. Des assureurs et des sociétés d'assistance internationales y gèrent leurs plateaux, car l'anglais est langue officielle et la main-d'&oelig;uvre parle de nombreuses langues. Les clients francophones &mdash; en France, en Belgique, en Suisse ou en Afrique du Nord &mdash; doivent être servis dans leur langue, ce qui rend les profils français/anglais très demandés.</p></section>
<section><h2>Le poste ouvert : Customer Contact Agent à Floriana</h2>
<p>Vous êtes le premier contact des assurés qui ont besoin d'aide pendant un voyage à l'étranger. Concrètement :</p>
<ul>
<li>répondre aux appels, e-mails et messages en ligne ;</li>
<li>ouvrir et suivre les dossiers dans le système interne ;</li>
<li>expliquer les procédures avec empathie et vérifier les polices d'assurance ;</li>
<li>travailler avec les autres services pour résoudre chaque demande dans les délais.</li></ul>
<p>Une expérience en service client, en assistance voyage ou en gestion de sinistres est un plus. Les étudiants en soins infirmiers ou en santé sont aussi encouragés à postuler. <a href="/jobs/customer-contact-agent/">Voir l'offre complète de Customer Contact Agent</a>.</p></section>
<div class="cta-box"><h2>Postulez aux offres service client à Malte</h2><p>Toutes nos offres en centre d'appels et service client, avec le salaire lorsqu'il est publié.</p><a href="{HUB}">Voir les emplois service client à Malte</a></div>
<section><h2>Salaire et conditions</h2>
<div class="article-table-wrap"><table class="check-table"><thead><tr><th>Élément</th><th>Customer Contact Agent</th></tr></thead><tbody>
<tr><td>Salaire</td><td>19 000 &ndash; 22 000 &euro; brut par an</td></tr>
<tr><td>Langues</td><td>Anglais + français, ou anglais + arabe + français</td></tr>
<tr><td>Horaires</td><td>40 h/semaine en rotation, week-ends et jours fériés compris</td></tr>
<tr><td>Lieu</td><td>Floriana, à côté de La Valette</td></tr>
<tr><td>Qui peut postuler</td><td>Résidents à Malte et citoyens européens</td></tr>
</tbody></table></div>
<p>Le salaire annoncé est brut : l'impôt sur le revenu et les cotisations sociales sont déduits. Estimez votre net avec notre <a href="/salary-calculator-malta">calculateur de salaire Malte</a>. Pour comparer avec d'autres postes, lisez notre article sur le <a href="/blog/call-centre-salary-malta">salaire en centre d'appels à Malte</a> (en anglais).</p></section>
<section><h2>Faut-il un permis de travail ?</h2>
<p>Les citoyens de l'Union européenne peuvent travailler librement à Malte. Les candidats hors UE ont besoin d'un permis de travail demandé par l'employeur ; vérifiez dans chaque offre la mention &laquo;&nbsp;qui peut postuler&nbsp;&raquo;, car certains postes sont réservés aux personnes résidant déjà à Malte.</p></section>
<section><h2>Comment postuler</h2>
<ul>
<li>Préparez un CV en anglais et indiquez clairement vos langues et votre niveau (langue maternelle, courant).</li>
<li>Postulez en ligne depuis l'offre ; notre équipe lit chaque candidature.</li>
<li>Attendez-vous à un court entretien téléphonique, souvent en partie en français, puis à un entretien avec le client.</li>
<li>Préparez-vous avec nos <a href="/blog/call-centre-interview-questions-malta">questions d'entretien pour centre d'appels</a> (en anglais).</li></ul></section>""",
    faqs=("Questions fréquentes", [
        ("Quel est le salaire d'un conseiller service client francophone à Malte ?",
         "Pour le poste de Customer Contact Agent que nous recrutons à Floriana, le salaire publié est de 19 000 &agrave; 22 000 &euro; brut par an."),
        ("Faut-il parler anglais pour travailler dans un centre d'appels à Malte ?",
         "Oui. L'anglais courant est obligatoire pour tous les postes, en plus du français."),
        ("Les débutants peuvent-ils postuler ?",
         "Une expérience en service client est un atout mais pas toujours obligatoire. Les étudiants en soins infirmiers ou en santé sont également encouragés à postuler."),
        ("Où trouver les offres en centre d'appels à Malte ?",
         "Toutes nos offres sont sur la page emplois service client à Malte d'Outreach Recruitment, avec le salaire lorsqu'il est publié."),
    ]),
    cta=("Trouvez votre emploi à Malte", "Consultez nos offres en service client et centre d'appels à Malte.", "Voir les offres service client"),
    related=["lavoro-call-center-malta-italiani", "language-requirements-customer-service-jobs-malta", "call-centre-salary-malta"],
    back="&larr; Retour au blog", read_more="À lire aussi",
))

# ------------------------------------------------------------------ 3. Italian guide
POSTS.append(dict(
    slug="lavoro-call-center-malta-italiani", lang="it", sub="career-planning",
    img=(W_IMG, (0, 1350, 1800, 2362)),
    title="Lavorare in un call center a Malta: guida per italiani",
    h1="Lavorare in un call center a Malta: la guida per italiani",
    desc="Lavoro nel servizio clienti e nei call center a Malta per chi parla italiano: posizioni aperte, stipendio 19.000–22.000 €, lingue, turni e candidatura.",
    alt="Operatrice di call center al computer con cuffie in un ufficio a Malta",
    keywords="lavoro call center Malta, lavorare a Malta italiani, servizio clienti Malta italiano, lavoro Malta italiano",
    tag="Lavoro a Malta", read=6,
    body=f"""<section><div class="answer-box"><strong>In breve:</strong> a Malta c'è richiesta costante di operatori del servizio clienti che parlano italiano. Il ruolo di <strong>Customer Contact Agent</strong> a Floriana, per cui stiamo selezionando, richiede inglese e italiano fluenti e offre <strong>19.000 &ndash; 22.000 &euro; lordi l'anno</strong>. Tutte le offerte sono nella pagina <a href="{HUB}">lavoro nel servizio clienti a Malta</a>.</div></section>
<section><h2>Punti chiave</h2><ul>
<li>L'inglese fluente è obbligatorio per tutte le posizioni; l'italiano è il tuo vantaggio principale.</li>
<li>Combinazione richiesta: inglese + italiano.</li>
<li>Stipendio pubblicato: 19.000 &ndash; 22.000 &euro; lordi l'anno, circa 1.580 &ndash; 1.830 &euro; lordi al mese.</li>
<li>Settimana di 40 ore su turni a rotazione, inclusi weekend e festivi.</li>
<li>Ci si candida online; il nostro team ti richiama per un primo colloquio telefonico.</li></ul></section>
<section><h2>Perché Malta cerca chi parla italiano</h2>
<p>Malta è uno dei principali hub europei per l'assistenza clienti multilingue. Assicurazioni e società di assistenza internazionali gestiscono qui i loro contact center perché l'inglese è lingua ufficiale e il personale parla molte lingue. I clienti italiani devono essere seguiti nella loro lingua, quindi i profili italiano/inglese sono molto ricercati &mdash; e Malta è a un'ora di volo dall'Italia.</p></section>
<section><h2>La posizione aperta: Customer Contact Agent a Floriana</h2>
<p>Sei il primo punto di contatto per gli assicurati che hanno bisogno di aiuto mentre sono all'estero. In pratica:</p>
<ul>
<li>gestisci chiamate, e-mail e canali online;</li>
<li>apri e aggiorni le pratiche nel sistema interno;</li>
<li>spieghi le procedure con empatia e verifichi le polizze;</li>
<li>collabori con gli altri reparti per risolvere ogni richiesta nei tempi previsti.</li></ul>
<p>L'esperienza nel servizio clienti, nell'assistenza viaggi o nella gestione sinistri è un plus; anche studenti di infermieristica o di corsi sanitari sono incoraggiati a candidarsi. <a href="/jobs/customer-contact-agent/">Leggi l'annuncio completo di Customer Contact Agent</a>.</p></section>
<div class="cta-box"><h2>Candidati per un lavoro nel servizio clienti a Malta</h2><p>Tutte le nostre offerte nei call center e nel servizio clienti, con lo stipendio quando pubblicato.</p><a href="{HUB}">Vedi i lavori nel servizio clienti a Malta</a></div>
<section><h2>Stipendio e condizioni</h2>
<div class="article-table-wrap"><table class="check-table"><thead><tr><th>Voce</th><th>Customer Contact Agent</th></tr></thead><tbody>
<tr><td>Stipendio</td><td>19.000 &ndash; 22.000 &euro; lordi l'anno</td></tr>
<tr><td>Lingue</td><td>Inglese + italiano</td></tr>
<tr><td>Orario</td><td>40 ore settimanali su turni, weekend e festivi inclusi</td></tr>
<tr><td>Sede</td><td>Floriana, accanto a La Valletta</td></tr>
<tr><td>Chi può candidarsi</td><td>Residenti a Malta e cittadini europei</td></tr>
</tbody></table></div>
<p>Lo stipendio indicato è lordo: imposte e contributi vengono trattenuti. Calcola il tuo netto con il nostro <a href="/salary-calculator-malta">calcolatore di stipendio per Malta</a>. Per confrontarlo con altri ruoli leggi la nostra guida allo <a href="/blog/call-centre-salary-malta">stipendio nei call center a Malta</a> (in inglese).</p></section>
<section><h2>Serve un permesso di lavoro?</h2>
<p>I cittadini italiani e dell'Unione europea possono lavorare liberamente a Malta. Chi non è cittadino UE ha bisogno di un permesso di lavoro richiesto dal datore di lavoro; controlla sempre la voce &laquo;chi può candidarsi&raquo; in ogni annuncio, perché alcune posizioni sono riservate a chi vive già a Malta.</p></section>
<section><h2>Come candidarsi</h2>
<ul>
<li>Prepara un CV in inglese e indica chiaramente le tue lingue e il livello (madrelingua, fluente).</li>
<li>Candidati online dall'annuncio; il nostro team legge ogni candidatura.</li>
<li>Aspettati una breve telefonata di selezione, spesso in parte in italiano, poi il colloquio con il cliente.</li>
<li>Preparati con le nostre <a href="/blog/call-centre-interview-questions-malta">domande di colloquio per call center</a> (in inglese).</li></ul></section>""",
    faqs=("Domande frequenti", [
        ("Quanto guadagna un operatore di call center che parla italiano a Malta?",
         "Per il ruolo di Customer Contact Agent a Floriana lo stipendio pubblicato è di 19.000 &ndash; 22.000 &euro; lordi l'anno."),
        ("Serve l'inglese per lavorare in un call center a Malta?",
         "Sì. L'inglese fluente è obbligatorio per tutte le posizioni, insieme all'italiano."),
        ("Posso candidarmi senza esperienza?",
         "L'esperienza nel servizio clienti è un vantaggio ma non sempre obbligatoria. Anche studenti di infermieristica o di corsi sanitari sono incoraggiati a candidarsi."),
        ("Dove trovo le offerte di lavoro nei call center a Malta?",
         "Tutte le nostre offerte sono nella pagina lavori nel servizio clienti a Malta di Outreach Recruitment, con lo stipendio quando pubblicato."),
    ]),
    cta=("Trova il tuo lavoro a Malta", "Scopri le nostre offerte nel servizio clienti e nei call center a Malta.", "Vedi le offerte nel servizio clienti"),
    related=["emploi-centre-appels-malte-francophones", "language-requirements-customer-service-jobs-malta", "call-centre-salary-malta"],
    back="&larr; Torna al blog", read_more="Leggi anche",
))

# ------------------------------------------------------------------ 4. interview questions
POSTS.append(dict(
    slug="call-centre-interview-questions-malta", lang="en", sub="job-interview",
    img=(M_IMG, (0, 300, 1800, 1312)),
    title="Call Centre Interview Questions in Malta (with Sample Answers)",
    h1="Call centre interview questions in Malta (with sample answers)",
    desc="The call centre and customer service interview questions Malta employers ask, with sample answers, a language-test checklist and tips to get hired.",
    alt="Smiling call centre agent with headset at his desk — call centre interview questions in Malta",
    keywords="call centre interview questions Malta, customer service interview questions, call agent interview Malta",
    tag="Candidates", read=7,
    body=f"""<section><div class="answer-box"><strong>Quick answer:</strong> Call centre interviews in Malta usually test four things: how you handle difficult customers, how you stay organised under pressure, whether you really work well in your languages, and whether the shift pattern suits you. Prepare short, real examples using the STAR method, and expect part of the interview in your second language. Ready to apply? See <a href="{HUB}">open call centre jobs in Malta</a>.</div></section>
<section><h2>Key Takeaways</h2><ul>
<li>Most processes have three steps: a phone screen, an interview with the employer, and sometimes a short role-play or language check.</li>
<li>Answer with real examples: Situation, Task, Action, Result.</li>
<li>If you list a language on your CV, expect to be tested in it.</li>
<li>Be honest about shifts &mdash; availability is a deciding factor for 24/7 desks.</li></ul></section>
<section><h2>How the interview process works</h2>
<p>When you apply through Outreach Recruitment, a consultant reviews your application personally and calls you for a short screen: your languages, your availability and why the role interests you. If you are a match, we arrange the interview with the client and brief you on what to expect. For multilingual desks, part of either call is often held in your second language.</p></section>
<section><h2>Common call centre interview questions and sample answers</h2>
<h3>1. &ldquo;Tell me about yourself.&rdquo;</h3>
<p>Keep it to 60 seconds: your customer-facing experience, your languages, and why this role. <em>Sample:</em> &ldquo;I've spent two years in hotel reception, handling check-ins and complaints in English and French. I enjoy solving problems for people under pressure, which is why an assistance desk appeals to me.&rdquo;</p>
<h3>2. &ldquo;Describe a time you dealt with an angry customer.&rdquo;</h3>
<p>Show that you listen, acknowledge, act and follow up. <em>Sample:</em> &ldquo;A guest was furious about a double charge. I let him finish, apologised for the stress, checked the booking while he was on the line, arranged the refund with accounts and emailed him confirmation the same day. He left a positive review.&rdquo;</p>
<h3>3. &ldquo;How do you handle several tasks at once?&rdquo;</h3>
<p>Talk about prioritising by urgency and keeping accurate notes. Case-handling roles in insurance and assistance care a lot about accurate records.</p>
<h3>4. &ldquo;What does good customer service mean to you?&rdquo;</h3>
<p>Go beyond &ldquo;being friendly&rdquo;: solving the problem first time, setting clear expectations and following up.</p>
<h3>5. &ldquo;How would you explain a complicated procedure to a stressed customer?&rdquo;</h3>
<p>Short steps, plain words, check understanding, and confirm in writing. This is central for roles like the <a href="/jobs/customer-contact-agent/">Customer Contact Agent</a>, where you explain insurance procedures to people who need help abroad.</p>
<h3>6. &ldquo;Are you comfortable working shifts, weekends and public holidays?&rdquo;</h3>
<p>Answer honestly. Many contact centre roles in Malta work rotating or 24/7 rotas &mdash; if you have limits, say so early.</p>
<h3>7. &ldquo;Why do you want to work in Malta / for this company?&rdquo;</h3>
<p>Mention something specific: the sector, the language desk, the training offered or the career path.</p>
<h3>8. &ldquo;What would you do if you didn't know the answer to a customer's question?&rdquo;</h3>
<p>Never guess. Explain that you would check the system or ask a colleague, tell the customer when they will hear back, and follow up.</p></section>
<div class="cta-box"><h2>Practise, then apply</h2><p>Customer service and call agent jobs in Malta for English, French, Italian, Arabic and Maltese speakers.</p><a href="{HUB}">See customer service vacancies in Malta</a></div>
<section><h2>The language check</h2>
<p>If you list French, Italian, Arabic or Maltese, expect the interviewer to switch language without warning, or to give you a short role-play call in it. Practise describing your last job and handling a complaint in each language you list. Our guide to <a href="/blog/language-requirements-customer-service-jobs-malta">language requirements for customer service jobs in Malta</a> explains the level employers expect.</p></section>
<section><h2>Questions to ask the interviewer</h2>
<ul>
<li>What does a typical shift look like, and how is the rota planned?</li>
<li>How long is the training, and is there a buddy system?</li>
<li>Which KPIs will I be measured on?</li>
<li>What does progression look like after the first year?</li></ul>
<p>For pay questions, read our guide to <a href="/blog/call-centre-salary-malta">call centre salaries in Malta</a> first so you know the realistic range. For general preparation, see <a href="/blog/what-to-expect-in-a-job-interview-in-malta">what to expect in a job interview in Malta</a>.</p></section>""",
    faqs=("FAQs", [
        ("What questions are asked in a call centre interview?",
         "Expect questions about handling difficult customers, multitasking, what good service means, explaining procedures clearly, and your availability for shifts. Multilingual roles usually include a language check."),
        ("Will my language skills be tested?",
         "Very likely. If you list a language on your CV, the interviewer may switch to it or give you a short role-play call in that language."),
        ("How should I answer behavioural questions?",
         "Use the STAR method: describe the Situation, your Task, the Action you took and the Result, using a real example."),
        ("Where can I apply for call centre jobs in Malta?",
         "Outreach Recruitment lists every open customer service and call centre job it recruits for on its customer service jobs in Malta page."),
    ]),
    cta=("Apply for a call centre job in Malta", "Open customer service, call centre and call agent roles, with salaries where published.", "View call centre jobs in Malta"),
    related=["call-centre-salary-malta", "language-requirements-customer-service-jobs-malta", "how-to-answer-common-interview-questions-in-malta"],
))

# ------------------------------------------------------------------ 5. language requirements
POSTS.append(dict(
    slug="language-requirements-customer-service-jobs-malta", lang="en", sub="career-planning",
    img=(M_IMG, (500, 60, 1800, 791)),
    title="Language Requirements for Customer Service Jobs in Malta",
    h1="Language requirements for customer service jobs in Malta",
    desc="Which languages do customer service and call centre jobs in Malta need? English, French, Italian, Arabic and Maltese requirements by role, and how to prove them.",
    alt="Customer service agent with headset at a computer — language requirements for customer service jobs in Malta",
    keywords="language requirements customer service Malta, multilingual jobs Malta, French speaking jobs Malta, Italian speaking jobs Malta",
    tag="Jobs in Malta", read=6,
    body=f"""<section><div class="answer-box"><strong>Quick answer:</strong> Every customer service job in Malta we recruit for requires <strong>fluent English</strong>. Many also need a second working language &mdash; French, Italian, Arabic or Maltese &mdash; and that second language is often what gets you hired. Find roles that match your languages on our <a href="{HUB}">customer service jobs in Malta</a> page.</div></section>
<section><h2>Key Takeaways</h2><ul>
<li>English is the working language of every contact centre in Malta.</li>
<li>&ldquo;Fluent&rdquo; means you can handle a full call, explain a procedure and write a clear email without help.</li>
<li>Second languages in demand in our listings: French, Italian, Arabic and Maltese.</li>
<li>Expect your languages to be tested during the interview.</li></ul></section>
<section><h2>Languages required by role</h2>
<div class="article-table-wrap"><table class="check-table"><thead><tr><th>Role</th><th>Languages required</th></tr></thead><tbody>
<tr><td><a href="/jobs/customer-contact-agent/">Customer Contact Agent</a></td><td>English + French, English + Italian, or English + Arabic + French</td></tr>
<tr><td><a href="/jobs/customer-contact-centre-representative/">Customer Contact Centre Representative</a></td><td>Fluent Maltese and English, written and spoken</td></tr>
<tr><td><a href="/jobs/assistance-operations-coordinator/">Assistance Operations Coordinator</a></td><td>Fluent English; Maltese an advantage</td></tr>
<tr><td><a href="/jobs/administration-specialist/">Administration Specialist</a></td><td>Excellent English; Maltese an asset</td></tr>
</tbody></table></div></section>
<section><h2>What &ldquo;fluent&rdquo; really means</h2>
<p>Employers rarely ask for a certificate. Instead, they check whether you can do the job in the language: understand a customer who is stressed or speaking fast, explain a policy or procedure in plain words, and write a clear, correct email. As a guide, that is roughly level C1 on the European (CEFR) scale. Native speakers and people who have studied or worked in the language are usually comfortable at this level.</p></section>
<div class="cta-box"><h2>Use your languages in Malta</h2><p>Multilingual customer service and call centre jobs for English, French, Italian, Arabic and Maltese speakers.</p><a href="{HUB}">Find multilingual customer service jobs in Malta</a></div>
<section><h2>Language guides for French and Italian speakers</h2>
<p>We have written dedicated guides in your language:</p>
<ul>
<li><a href="/blog/emploi-centre-appels-malte-francophones" lang="fr">Travailler dans un centre d'appels à Malte : guide pour francophones</a></li>
<li><a href="/blog/lavoro-call-center-malta-italiani" lang="it">Lavorare in un call center a Malta: guida per italiani</a></li></ul></section>
<section><h2>How to show your languages on your CV</h2>
<ul>
<li>List each language with an honest level: native, fluent, conversational.</li>
<li>Give proof: years lived, studied or worked in the language, or a certificate if you have one.</li>
<li>Mention the channels you can work in &mdash; phone, email, chat.</li>
<li>Put languages near the top of your CV; for multilingual desks they matter more than anything else.</li></ul></section>
<section><h2>Do I need to speak Maltese?</h2>
<p>Only for roles that serve the local market, like the Maltese-speaking Customer Contact Centre Representative. For most international desks Maltese is an advantage, not a requirement. English is an official language in Malta, so you can live and work here comfortably in English.</p>
<p>Languages also affect pay &mdash; see our guide to <a href="/blog/call-centre-salary-malta">call centre salaries in Malta</a>, and prepare for the language check with our <a href="/blog/call-centre-interview-questions-malta">call centre interview questions</a>.</p></section>""",
    faqs=("FAQs", [
        ("Do I need English for customer service jobs in Malta?",
         "Yes. Fluent English is required for every customer service and call centre role we recruit for in Malta."),
        ("Which second languages are most in demand?",
         "In our current listings: French, Italian, Arabic and Maltese. The Customer Contact Agent role accepts English with French, Italian, or Arabic and French."),
        ("Do I need a language certificate?",
         "Usually not. Employers test your language during the interview instead. A certificate can still help prove your level on your CV."),
        ("Is Maltese required to work in a Malta call centre?",
         "Only for roles serving the local market, such as the Maltese-speaking Customer Contact Centre Representative. For other roles Maltese is an advantage, not a requirement."),
    ]),
    cta=("Find a job that uses your languages", "Customer service and call centre jobs in Malta for multilingual candidates.", "Browse customer service jobs in Malta"),
    related=["emploi-centre-appels-malte-francophones", "lavoro-call-center-malta-italiani", "call-centre-interview-questions-malta"],
))


# ================================================================== build
TITLES = {p["slug"]: p["h1"] for p in POSTS}


def card_image(slug):
    for ext in ("jpg", "png"):
        if (ROOT / "assets" / "blog-featured" / f"{slug}.{ext}").exists():
            return f"/assets/blog-featured/{slug}.{ext}"
    return None


def make_image(p):
    src, box = p["img"]
    out = ROOT / "assets" / "blog-featured" / f"{p['slug']}.jpg"
    im = Image.open(src).convert("RGB").crop(box).resize((1600, 900), Image.LANCZOS)
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    return f"/assets/blog-featured/{p['slug']}.jpg"


tpl = TEMPLATE.read_text()
first_faq = re.search(r'<div class="faq-item">.*?</p></div></div></div>', tpl, re.S).group(0)
faq_tpl = re.sub(r'(<h3 class="text-large strong">).*?(</h3>)', r'\1@@Q@@\2', first_faq, flags=re.S)
faq_tpl = re.sub(r'(<p class="text-medium">).*?(</p>)', r'\1@@A@@\2', faq_tpl, flags=re.S)
head_end = tpl.index("<!-- Google tag (gtag.js) -->")
head_style = re.search(r"<style>.*?</style>", tpl[:head_end], re.S).group(0)
main_start, main_end = tpl.index('<main class="main">'), tpl.index("</main>")


def plain(s):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def build(p):
    url = f"{BASE}/blog/{p['slug']}"
    img = make_image(p)
    img_abs = BASE + img
    e = H.escape
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": f"{BASE}/#organization", "name": "Outreach Recruitment Ltd", "url": f"{BASE}/",
         "logo": {"@type": "ImageObject", "url": f"{BASE}/assets/outreach-recruitment-logo.svg"}},
        {"@type": "BlogPosting", "@id": f"{url}#article", "headline": p["h1"], "description": p["desc"], "url": url,
         "image": {"@type": "ImageObject", "url": img_abs, "width": 1600, "height": 900},
         "datePublished": f"{DATE}T00:00:00Z", "dateModified": f"{DATE}T00:00:00Z",
         "author": {"@id": f"{BASE}/#organization"}, "publisher": {"@id": f"{BASE}/#organization"},
         "inLanguage": p["lang"], "keywords": p["keywords"],
         "about": {"@type": "WebPage", "name": "Customer Service Jobs in Malta", "url": f"{BASE}{HUB}"},
         "mainEntityOfPage": {"@type": "WebPage", "@id": url}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{BASE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["h1"], "item": url}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}}
                                            for q, a in p["faqs"][1]]}]}
    head = f"""<!DOCTYPE html>
<html lang="{p['lang']}">
<head>
  <meta charset="utf-8"/>
  <title>{e(p['title'])}</title>
  <meta name="description" content="{e(p['desc'])}"/>
  <meta property="og:title" content="{e(p['h1'])}"/>
  <meta property="og:description" content="{e(p['desc'])}"/>
  <meta property="og:image" content="{img_abs}"/>
  <meta property="og:image:width" content="1600"/>
  <meta property="og:image:height" content="900"/>
  <meta property="og:image:type" content="image/jpeg"/>
  <meta property="og:image:alt" content="{e(p['alt'])}"/>
  <meta property="og:type" content="article"/>
  <meta property="og:url" content="{url}"/>
  <meta property="og:site_name" content="Outreach Recruitment Agency"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <meta name="twitter:title" content="{e(p['h1'])}"/>
  <meta name="twitter:description" content="{e(p['desc'])}"/>
  <meta name="twitter:image" content="{img_abs}"/>
  <link rel="canonical" href="{url}"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <link rel="preconnect" href="https://cdn.prod.website-files.com" crossorigin/>
  <link rel="dns-prefetch" href="https://cdn.prod.website-files.com"/>
  <link crossorigin="anonymous" href="https://cdn.prod.website-files.com/6996b31b0e199fa8510adf4f/css/people-work-webflow-108-template.webflow.shared.6c8c6beff.css" integrity="sha384-bIxr7/VAGMc1npTdLY7+pxf0nBYi2449/GvW5FYUfyx/ZQEFNpXpICDcC/gSarqa" rel="stylesheet" type="text/css"/>
  <link href="/assets/brand-overrides.css" rel="stylesheet" type="text/css"/>
  <link href="/assets/job-card-logo.jpg" rel="icon" type="image/jpeg"/>
  <link href="/assets/job-card-logo.jpg" rel="apple-touch-icon"/>
  {head_style}
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
"""
    date_label = {"fr": "9 octobre 2026", "it": "9 ottobre 2026"}.get(p["lang"], DATE_EN)
    related = "".join(
        f'<a class="article-card w-inline-block" href="/blog/{s}"><img src="{card_image(s)}" alt="{e(TITLES.get(s) or plain(related_title(s)))}" loading="lazy">'
        f'<div class="article-card-content"><div class="caption blue-caption">Candidates</div><h3 class="heading-h5">{TITLES.get(s) or related_title(s)}</h3></div></a>'
        for s in p["related"] if card_image(s))
    main = f"""<main class="main">
    <section class="section page-header">
      <div class="w-layout-blockcontainer container w-container">
        <div class="w-layout-vflex section-content">
          <div class="w-layout-vflex text center" data-gsap-scroll="text">
            <a href="/blog/" style="display:inline-flex;align-items:center;gap:0.35rem;font-size:0.85rem;color:#442DFA;text-decoration:none;margin-bottom:0.9rem;font-weight:600;">{p.get('back', '&larr; Back to Blog')}</a>
            <div class="tag darker">{p['tag']}</div>
            <h1 class="heading-h1">{p['h1']}</h1>
            <div class="caption blue-caption">{date_label}</div>
          </div>
          <div class="cms-featured-media" data-gsap-scroll="fade"><img src="{img}" alt="{e(p['alt'])}" class="media-fill" width="1600" height="900" fetchpriority="high" sizes="100vw"/></div>
        </div>
      </div>
    </section>
    <section class="section padding-top-extra-small">
      <div class="w-layout-blockcontainer container tight w-container">
        <article class="cms-article">
          <div class="w-richtext">{p['body']}{faq_html(p['faqs'], faq_tpl)}<div class="cta-box"><h2>{p['cta'][0]}</h2><p>{p['cta'][1]}</p><a href="{HUB}">{p['cta'][2]}</a></div></div>
        </article>
        <section>
          <h2 class="heading-h3">{p.get('read_more', 'Read more')}</h2>
          <div class="related-grid">{related}</div>
        </section>
      </div>
    </section>
  """
    out = head + tpl[head_end:main_start] + main + tpl[main_end:]
    out = out.replace('<html lang="en">', f'<html lang="{p["lang"]}">', 1)
    (ROOT / "blog" / f"{p['slug']}.html").write_text(out)
    return img


def related_title(slug):
    t = (ROOT / "blog" / f"{slug}.html").read_text()
    return re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S).group(1).strip()


def add_index_cards(images):
    idx_path = ROOT / "blog" / "index.html"
    s = idx_path.read_text()
    sec = s.index('data-blog-section="candidates"')
    grid = s.index('<div class="articles-grid w-dyn-items"', sec)
    grid_open_end = s.index(">", grid) + 1
    tpl_card = re.search(r'<article class="article-card w-dyn-item".*?</article>', s[grid:], re.S).group(0)
    old_slug = re.search(r'data-blog-subcategory="([^"]+)"', tpl_card).group(1)
    old_img = re.search(r'<img src="([^"]+)" alt="([^"]*)"', tpl_card)
    old_h = re.search(r'<h3 class="heading-h6 capitalize">(.*?)</h3>', tpl_card).group(1)
    old_date = re.search(r'<div class="text-small"[^>]*>(.*?)</div>', tpl_card).group(1)
    old_tag = re.search(r'<div class="tag darker">(.*?)</div>', tpl_card).group(1)
    new = ""
    for p in POSTS:
        if f'href="/blog/{p["slug"]}.html"' in s:
            continue
        c = tpl_card.replace(f'data-blog-subcategory="{old_slug}"', f'data-blog-subcategory="{p["sub"]}"')
        c = c.replace(f"/blog/{old_slug}.html", f"/blog/{p['slug']}.html")
        c = c.replace(f'<img src="{old_img.group(1)}" alt="{old_img.group(2)}"', f'<img src="{images[p["slug"]]}" alt="{H.escape(p["alt"])}"')
        c = c.replace(f'<h3 class="heading-h6 capitalize">{old_h}</h3>', f'<h3 class="heading-h6 capitalize">{p["h1"]}</h3>')
        c = c.replace(f">{old_date}</div>", f">{DATE_EN} &middot; {p['read']} min read</div>")
        c = c.replace(f'<div class="tag darker">{old_tag}</div>', '<div class="tag darker">Candidates</div>')
        new += c
    s = s[:grid_open_end] + new + s[grid_open_end:]
    idx_path.write_text(s)
    return new.count("<article")


def add_sitemaps(images):
    sm = ROOT / "sitemaps" / "sitemap-blog.xml"
    s = sm.read_text()
    add = "".join(f"""
  <url>
    <loc>{BASE}/blog/{p['slug']}</loc>
    <lastmod>{DATE}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
""" for p in POSTS if f"/blog/{p['slug']}</loc>" not in s)
    if add:
        sm.write_text(s.replace("</urlset>", add + "</urlset>"))
    smi = ROOT / "sitemaps" / "sitemap-blog-images.xml"
    s = smi.read_text()
    add = "".join(f"""  <url>
    <loc>{BASE}/blog/{p['slug']}</loc>
    <lastmod>{DATE}</lastmod>
    <image:image>
      <image:loc>{BASE}{images[p['slug']]}</image:loc>
    </image:image>
  </url>
""" for p in POSTS if f"/blog/{p['slug']}</loc>" not in s)
    if add:
        smi.write_text(s.replace("</urlset>", add + "</urlset>"))


if __name__ == "__main__":
    images = {}
    for p in POSTS:
        images[p["slug"]] = make_image(p)
    for p in POSTS:
        build(p)
        print("written blog/%s.html" % p["slug"])
    print("index cards added:", add_index_cards(images))
    add_sitemaps(images)
