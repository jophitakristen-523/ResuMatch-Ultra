import os
import json
import anthropic
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
MODEL = "claude-sonnet-4-20250514"

COUNTRIES = {
    "North America": [
        {
            "code": "US", "name": "United States", "flag": "\U0001f1fa\U0001f1f8",
            "cities": ["New York", "San Francisco", "Seattle", "Austin", "Boston", "Chicago", "Los Angeles", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "\U0001f4bc", "desc": "World's largest professional network", "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}"},
                {"name": "Indeed",    "icon": "\U0001f50d", "desc": "Millions of jobs worldwide",           "rating": 4.5, "color": "#003a9b", "urlTemplate": "https://www.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Glassdoor", "icon": "\u2b50",    "desc": "Jobs + company reviews",               "rating": 4.3, "color": "#0caa41", "urlTemplate": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={skills}"},
                {"name": "Wellfound", "icon": "\U0001f680", "desc": "Top startup jobs",                    "rating": 4.4, "color": "#fb4a00", "urlTemplate": "https://wellfound.com/jobs?q={skills}&l={loc}"},
                {"name": "Dice",      "icon": "\U0001f3b2", "desc": "Tech jobs specialist",                "rating": 4.0, "color": "#e53935", "urlTemplate": "https://www.dice.com/jobs?q={skills}&location={loc}"},
                {"name": "Hired",     "icon": "\U0001f91d", "desc": "Tech talent marketplace",             "rating": 4.2, "color": "#7c4dff", "urlTemplate": "https://hired.com/jobs?q={skills}"},
            ],
        },
        {
            "code": "CA", "name": "Canada", "flag": "\U0001f1e8\U0001f1e6",
            "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa", "Remote"],
            "boards": [
                {"name": "LinkedIn",   "icon": "\U0001f4bc", "desc": "Professional network",      "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Canada"},
                {"name": "Indeed CA",  "icon": "\U0001f50d", "desc": "Canada's top job board",    "rating": 4.5, "color": "#003a9b", "urlTemplate": "https://ca.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Workopolis", "icon": "\U0001f341", "desc": "Canadian job search",       "rating": 4.0, "color": "#e53935", "urlTemplate": "https://www.workopolis.com/jobsearch/find-jobs?ak={skills}&l={loc}"},
                {"name": "JobBank",    "icon": "\U0001f3db", "desc": "Government of Canada jobs", "rating": 4.2, "color": "#d32f2f", "urlTemplate": "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={skills}&locationstring={loc}"},
            ],
        },
    ],
    "Europe": [
        {
            "code": "GB", "name": "United Kingdom", "flag": "\U0001f1ec\U0001f1e7",
            "cities": ["London", "Manchester", "Edinburgh", "Bristol", "Birmingham", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "\U0001f4bc", "desc": "Professional network",  "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+UK"},
                {"name": "Reed",      "icon": "\U0001f33f", "desc": "UK's #1 job site",      "rating": 4.6, "color": "#d62b2b", "urlTemplate": "https://www.reed.co.uk/jobs/{skills}-jobs-in-{loc}"},
                {"name": "Totaljobs", "icon": "\U0001f4cb", "desc": "UK job search leader",  "rating": 4.3, "color": "#ff6b35", "urlTemplate": "https://www.totaljobs.com/jobs/{skills}/in-{loc}"},
                {"name": "CWJobs",    "icon": "\U0001f4bb", "desc": "UK tech specialists",   "rating": 4.1, "color": "#0072bc", "urlTemplate": "https://www.cwjobs.co.uk/jobs/{skills}/in-{loc}"},
            ],
        },
        {
            "code": "DE", "name": "Germany", "flag": "\U0001f1e9\U0001f1ea",
            "cities": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "\U0001f4bc", "desc": "Professional network",         "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Germany"},
                {"name": "StepStone", "icon": "\U0001fab9", "desc": "Germany's leading job board",  "rating": 4.5, "color": "#f60",    "urlTemplate": "https://www.stepstone.de/jobs/{skills}/in-{loc}.html"},
                {"name": "XING",      "icon": "\u2716",    "desc": "German professional network",   "rating": 4.2, "color": "#026466", "urlTemplate": "https://www.xing.com/jobs/search?keywords={skills}&location={loc}"},
                {"name": "Indeed DE", "icon": "\U0001f50d", "desc": "German job search",            "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://de.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
        {
            "code": "FR", "name": "France", "flag": "\U0001f1eb\U0001f1f7",
            "cities": ["Paris", "Lyon", "Marseille", "Toulouse", "Remote"],
            "boards": [
                {"name": "LinkedIn",              "icon": "\U0001f4bc", "desc": "Professional network", "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+France"},
                {"name": "Indeed FR",             "icon": "\U0001f50d", "desc": "French job search",    "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://fr.indeed.com/emplois?q={skills}&l={loc}"},
                {"name": "Welcome to the Jungle", "icon": "\U0001f33f", "desc": "French startup jobs",  "rating": 4.5, "color": "#1DB954", "urlTemplate": "https://www.welcometothejungle.com/fr/jobs?query={skills}"},
            ],
        },
        {
            "code": "ES", "name": "Spain", "flag": "\U0001f1ea\U0001f1f8",
            "cities": ["Madrid", "Barcelona", "Valencia", "Seville", "Remote"],
            "boards": [
                {"name": "LinkedIn", "icon": "\U0001f4bc", "desc": "Professional network",   "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Spain"},
                {"name": "Infojobs", "icon": "\u2139",    "desc": "Spain's top job board",   "rating": 4.5, "color": "#009fe3", "urlTemplate": "https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword={skills}&city={loc}"},
                {"name": "Indeed ES","icon": "\U0001f50d", "desc": "Spanish job search",     "rating": 4.3, "color": "#003a9b", "urlTemplate": "https://es.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
    ],
    "Asia Pacific": [
        {
            "code": "IN", "name": "India", "flag": "\U0001f1ee\U0001f1f3",
            "cities": ["Bangalore", "Mumbai", "Hyderabad", "Pune", "Chennai", "Delhi", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "\U0001f4bc", "desc": "Professional network",     "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+India"},
                {"name": "Naukri",    "icon": "\U0001f536", "desc": "India's #1 job portal",    "rating": 4.7, "color": "#fd7e00", "urlTemplate": "https://www.naukri.com/{skills}-jobs-in-{loc}"},
                {"name": "Indeed IN", "icon": "\U0001f50d", "desc": "Indian job search",        "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://in.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Shine",     "icon": "\u2728",    "desc": "Leading Indian job board",  "rating": 4.2, "color": "#00bfa5", "urlTemplate": "https://www.shine.com/job-search/{skills}-jobs-in-{loc}"},
                {"name": "Wellfound", "icon": "\U0001f680", "desc": "Startup jobs India",       "rating": 4.3, "color": "#fb4a00", "urlTemplate": "https://wellfound.com/jobs?q={skills}&l=India"},
                {"name": "Instahyre", "icon": "\u26a1",    "desc": "AI-powered hiring India",   "rating": 4.4, "color": "#7c4dff", "urlTemplate": "https://www.instahyre.com/search-jobs/?keywords={skills}&location={loc}"},
            ],
        },
        {
            "code": "SG", "name": "Singapore", "flag": "\U0001f1f8\U0001f1ec",
            "cities": ["Singapore", "Remote"],
            "boards": [
                {"name": "LinkedIn",        "icon": "\U0001f4bc", "desc": "Professional network",       "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location=Singapore"},
                {"name": "JobsDB",          "icon": "\U0001f4f1", "desc": "Asia's top job board",       "rating": 4.5, "color": "#e53935", "urlTemplate": "https://sg.jobsdb.com/j?q={skills}&l=Singapore"},
                {"name": "MyCareersFuture", "icon": "\U0001f1f8\U0001f1ec", "desc": "Singapore government jobs", "rating": 4.6, "color": "#d62b2b", "urlTemplate": "https://www.mycareersfuture.gov.sg/search?search={skills}"},
                {"name": "Indeed SG",       "icon": "\U0001f50d", "desc": "Singapore job search",       "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://sg.indeed.com/jobs?q={skills}&l=Singapore"},
            ],
        },
        {
            "code": "AU", "name": "Australia", "flag": "\U0001f1e6\U0001f1fa",
            "cities": ["Sydney", "Melbourne", "Brisbane", "Perth", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "\U0001f4bc", "desc": "Professional network",      "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Australia"},
                {"name": "Seek",      "icon": "\U0001f50e", "desc": "Australia's #1 job site",   "rating": 4.8, "color": "#e60278", "urlTemplate": "https://www.seek.com.au/{skills}-jobs/in-{loc}"},
                {"name": "Indeed AU", "icon": "\U0001f50d", "desc": "Australian job search",     "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://au.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Jora",      "icon": "\U0001f998", "desc": "Australian job aggregator", "rating": 4.1, "color": "#ff6b35", "urlTemplate": "https://au.jora.com/j?q={skills}&l={loc}"},
            ],
        },
        {
            "code": "JP", "name": "Japan", "flag": "\U0001f1ef\U0001f1f5",
            "cities": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "\U0001f4bc", "desc": "Professional network",  "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Japan"},
                {"name": "Gaijinpot", "icon": "\U0001f5fe", "desc": "English jobs in Japan", "rating": 4.4, "color": "#e53935", "urlTemplate": "https://jobs.gaijinpot.com/index/index/search?language=1&keywords={skills}"},
                {"name": "Indeed JP", "icon": "\U0001f50d", "desc": "Japan job search",      "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://jp.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
    ],
    "Middle East & Africa": [
        {
            "code": "AE", "name": "UAE", "flag": "\U0001f1e6\U0001f1ea",
            "cities": ["Dubai", "Abu Dhabi", "Sharjah", "Remote"],
            "boards": [
                {"name": "LinkedIn",   "icon": "\U0001f4bc", "desc": "Professional network",   "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+UAE"},
                {"name": "Bayt",       "icon": "\U0001f319", "desc": "MENA's top job board",   "rating": 4.6, "color": "#00a651", "urlTemplate": "https://www.bayt.com/en/uae/jobs/{skills}-jobs/"},
                {"name": "GulfTalent", "icon": "\U0001f3c6", "desc": "Gulf professional jobs", "rating": 4.4, "color": "#ff6b35", "urlTemplate": "https://www.gulftalent.com/jobs?search%5Bkeywords%5D={skills}"},
                {"name": "Indeed AE",  "icon": "\U0001f50d", "desc": "UAE job search",         "rating": 4.3, "color": "#003a9b", "urlTemplate": "https://ae.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
        {
            "code": "ZA", "name": "South Africa", "flag": "\U0001f1ff\U0001f1e6",
            "cities": ["Johannesburg", "Cape Town", "Durban", "Remote"],
            "boards": [
                {"name": "LinkedIn",       "icon": "\U0001f4bc", "desc": "Professional network",         "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+South+Africa"},
                {"name": "PNet",           "icon": "\U0001f30d", "desc": "South Africa's top job board", "rating": 4.5, "color": "#e53935", "urlTemplate": "https://www.pnet.co.za/jobs/{skills}-jobs/in-{loc}/"},
                {"name": "CareerJunction", "icon": "\U0001f500", "desc": "SA career portal",             "rating": 4.3, "color": "#0072bc", "urlTemplate": "https://www.careerjunction.co.za/jobs/results?keywords={skills}"},
            ],
        },
    ],
    "Latin America": [
        {
            "code": "BR", "name": "Brazil", "flag": "\U0001f1e7\U0001f1f7",
            "cities": ["Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Remote"],
            "boards": [
                {"name": "LinkedIn", "icon": "\U0001f4bc", "desc": "Professional network",       "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Brazil"},
                {"name": "Catho",    "icon": "\U0001f431", "desc": "Brazil's leading job board", "rating": 4.4, "color": "#e53935", "urlTemplate": "https://www.catho.com.br/vagas/{skills}/"},
                {"name": "Indeed BR","icon": "\U0001f50d", "desc": "Brazilian job search",       "rating": 4.3, "color": "#003a9b", "urlTemplate": "https://br.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Gupy",     "icon": "\U0001f680", "desc": "Brazilian HR tech platform", "rating": 4.5, "color": "#7c4dff", "urlTemplate": "https://portal.gupy.io/job-search?term={skills}"},
            ],
        },
        {
            "code": "MX", "name": "Mexico", "flag": "\U0001f1f2\U0001f1fd",
            "cities": ["Mexico City", "Guadalajara", "Monterrey", "Remote"],
            "boards": [
                {"name": "LinkedIn",    "icon": "\U0001f4bc", "desc": "Professional network",   "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Mexico"},
                {"name": "OCC Mundial", "icon": "\U0001f30e", "desc": "Mexico's top job board", "rating": 4.5, "color": "#d62b2b", "urlTemplate": "https://www.occ.com.mx/empleos/de-{skills}/en-{loc}/"},
                {"name": "Indeed MX",   "icon": "\U0001f50d", "desc": "Mexican job search",     "rating": 4.3, "color": "#003a9b", "urlTemplate": "https://mx.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
    ],
}


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_client():
    """Lazy Anthropic client — never crashes at startup."""
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


def ask_claude(system_prompt, user_message, max_tokens=2000):
    """Call Claude and return parsed JSON dict or list."""
    msg = get_client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()
    return json.loads(raw)


# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", countries=COUNTRIES)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/analyze", methods=["POST"])
def analyze():
    body    = request.get_json(force=True)
    resume  = (body.get("resume")  or "").strip()
    country = (body.get("country") or "").strip()
    city    = (body.get("city")    or "Any City").strip()

    if not resume:
        return jsonify({"error": "Resume text is required."}), 400
    if not country:
        return jsonify({"error": "Country is required."}), 400

    system = (
        "You are an expert resume parser and job-matching AI.\n\n"
        "Given a resume, target country, and optional city:\n"
        "1. Extract every technical and soft skill.\n"
        "2. Infer the most likely job role/title.\n"
        "3. Identify skills commonly required for that role that are MISSING.\n"
        "4. Provide a realistic local salary range for that country.\n"
        "5. Generate 6-8 realistic varied job listings for that country/city.\n\n"
        "Return ONLY valid JSON with these exact keys:\n"
        '{"skills":["..."],"role":"...","confidence":85,"missing":["..."],"salaryRef":"...","jobs":[{'
        '"title":"...","company":"...","score":0.87,"skillScore":0.75,"companyRating":4.2,'
        '"salary":"...","location":"...","remote":true,"experience":"3-5 years",'
        '"requiredSkills":["..."],"matched":["..."],"missing":["..."],"niceToHave":["..."],'
        '"snippet":"...","linkedinUrl":"...","indeedUrl":"...","googleJobsUrl":"...",'
        '"glassdoorUrl":"...","wellfoundUrl":"..."}]}'
    )
    user = f"Resume:\n{resume}\n\nTarget country: {country}\nPreferred city: {city}"

    try:
        data = ask_claude(system, user, max_tokens=3000)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)


@app.route("/api/review", methods=["POST"])
def review():
    job  = request.get_json(force=True)
    system = (
        "You are a friendly expert career coach. Given a job match object, write:\n"
        "- A concise honest encouraging 2-3 sentence review explaining the fit.\n"
        "- 3-5 priority skills the candidate should develop for this role.\n\n"
        'Return ONLY valid JSON: {"review":"...","prioritySkills":["..."]}'
    )
    user = f"Job details:\n{json.dumps(job, indent=2)}"
    try:
        data = ask_claude(system, user, max_tokens=600)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(data)


@app.route("/api/roadmap", methods=["POST"])
def roadmap():
    body           = request.get_json(force=True)
    role           = (body.get("role") or "").strip()
    missing_skills = body.get("missingSkills") or []
    user_skills    = body.get("userSkills")    or []

    if not role or not missing_skills:
        return jsonify([])

    system = (
        "You are a senior engineering mentor. Given a target role, missing skills, and known skills,\n"
        "produce a learning roadmap sorted by career impact (highest first).\n\n"
        "Return ONLY a valid JSON array:\n"
        '[{"skill":"...","why":"one sentence","priority":95,"weeks":3,'
        '"resources":[{"name":"...","url":"...","platform":"..."}]}]'
    )
    user = (
        f"Target role: {role}\n"
        f"Skills to learn: {', '.join(missing_skills[:7])}\n"
        f"Skills already known: {', '.join(user_skills)}"
    )
    try:
        data = ask_claude(system, user, max_tokens=2500)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if isinstance(data, dict):
        data = list(data.values())[0] if data else []
    return jsonify(data)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
