import os
import json
import anthropic
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-opus-4-5"

# ─────────────────────────────────────────────
#  COUNTRIES DATA
# ─────────────────────────────────────────────
COUNTRIES = {
    "North America": [
        {
            "code": "US", "name": "United States", "flag": "🇺🇸",
            "cities": ["New York", "San Francisco", "Seattle", "Austin", "Boston", "Chicago", "Los Angeles", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "💼", "desc": "World's largest professional network", "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}"},
                {"name": "Indeed",    "icon": "🔍", "desc": "Millions of jobs worldwide",           "rating": 4.5, "color": "#003a9b", "urlTemplate": "https://www.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Glassdoor", "icon": "⭐", "desc": "Jobs + company reviews",              "rating": 4.3, "color": "#0caa41", "urlTemplate": "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={skills}"},
                {"name": "Wellfound", "icon": "🚀", "desc": "Top startup jobs",                    "rating": 4.4, "color": "#fb4a00", "urlTemplate": "https://wellfound.com/jobs?q={skills}&l={loc}"},
                {"name": "Dice",      "icon": "🎲", "desc": "Tech jobs specialist",                "rating": 4.0, "color": "#e53935", "urlTemplate": "https://www.dice.com/jobs?q={skills}&location={loc}"},
                {"name": "Hired",     "icon": "🤝", "desc": "Tech talent marketplace",             "rating": 4.2, "color": "#7c4dff", "urlTemplate": "https://hired.com/jobs?q={skills}"},
            ],
        },
        {
            "code": "CA", "name": "Canada", "flag": "🇨🇦",
            "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa", "Remote"],
            "boards": [
                {"name": "LinkedIn",   "icon": "💼", "desc": "Professional network",      "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Canada"},
                {"name": "Indeed CA",  "icon": "🔍", "desc": "Canada's top job board",    "rating": 4.5, "color": "#003a9b", "urlTemplate": "https://ca.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Workopolis", "icon": "🍁", "desc": "Canadian job search",       "rating": 4.0, "color": "#e53935", "urlTemplate": "https://www.workopolis.com/jobsearch/find-jobs?ak={skills}&l={loc}"},
                {"name": "JobBank",    "icon": "🏛️", "desc": "Government of Canada jobs", "rating": 4.2, "color": "#d32f2f", "urlTemplate": "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={skills}&locationstring={loc}"},
            ],
        },
    ],
    "Europe": [
        {
            "code": "GB", "name": "United Kingdom", "flag": "🇬🇧",
            "cities": ["London", "Manchester", "Edinburgh", "Bristol", "Birmingham", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "💼", "desc": "Professional network",  "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+UK"},
                {"name": "Reed",      "icon": "🌿", "desc": "UK's #1 job site",      "rating": 4.6, "color": "#d62b2b", "urlTemplate": "https://www.reed.co.uk/jobs/{skills}-jobs-in-{loc}"},
                {"name": "Totaljobs", "icon": "📋", "desc": "UK job search leader",  "rating": 4.3, "color": "#ff6b35", "urlTemplate": "https://www.totaljobs.com/jobs/{skills}/in-{loc}"},
                {"name": "CWJobs",    "icon": "💻", "desc": "UK tech specialists",   "rating": 4.1, "color": "#0072bc", "urlTemplate": "https://www.cwjobs.co.uk/jobs/{skills}/in-{loc}"},
            ],
        },
        {
            "code": "DE", "name": "Germany", "flag": "🇩🇪",
            "cities": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "💼", "desc": "Professional network",          "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Germany"},
                {"name": "StepStone", "icon": "🪜", "desc": "Germany's leading job board",  "rating": 4.5, "color": "#f60",    "urlTemplate": "https://www.stepstone.de/jobs/{skills}/in-{loc}.html"},
                {"name": "XING",      "icon": "✖️", "desc": "German professional network", "rating": 4.2, "color": "#026466", "urlTemplate": "https://www.xing.com/jobs/search?keywords={skills}&location={loc}"},
                {"name": "Indeed DE", "icon": "🔍", "desc": "German job search",            "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://de.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
        {
            "code": "NL", "name": "Netherlands", "flag": "🇳🇱",
            "cities": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Remote"],
            "boards": [
                {"name": "LinkedIn",               "icon": "💼", "desc": "Professional network", "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Netherlands"},
                {"name": "Nationale Vacaturebank", "icon": "🌷", "desc": "Top Dutch job board",  "rating": 4.3, "color": "#ff6b35", "urlTemplate": "https://www.nationalevacaturebank.nl/vacature/zoeken?query={skills}&location={loc}"},
                {"name": "Monsterboard",           "icon": "👾", "desc": "Dutch job search",     "rating": 4.0, "color": "#7c00f0", "urlTemplate": "https://www.monsterboard.nl/vacatures/zoeken?q={skills}&where={loc}"},
            ],
        },
        {
            "code": "FR", "name": "France", "flag": "🇫🇷",
            "cities": ["Paris", "Lyon", "Marseille", "Toulouse", "Remote"],
            "boards": [
                {"name": "LinkedIn",               "icon": "💼", "desc": "Professional network", "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+France"},
                {"name": "Indeed FR",              "icon": "🔍", "desc": "French job search",    "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://fr.indeed.com/emplois?q={skills}&l={loc}"},
                {"name": "Welcome to the Jungle",  "icon": "🌿", "desc": "French startup jobs",  "rating": 4.5, "color": "#1DB954", "urlTemplate": "https://www.welcometothejungle.com/fr/jobs?query={skills}"},
            ],
        },
        {
            "code": "ES", "name": "Spain", "flag": "🇪🇸",
            "cities": ["Madrid", "Barcelona", "Valencia", "Seville", "Remote"],
            "boards": [
                {"name": "LinkedIn", "icon": "💼", "desc": "Professional network",   "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Spain"},
                {"name": "Infojobs", "icon": "ℹ️", "desc": "Spain's top job board", "rating": 4.5, "color": "#009fe3", "urlTemplate": "https://www.infojobs.net/jobsearch/search-results/list.xhtml?keyword={skills}&city={loc}"},
                {"name": "Indeed ES","icon": "🔍", "desc": "Spanish job search",    "rating": 4.3, "color": "#003a9b", "urlTemplate": "https://es.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
    ],
    "Asia Pacific": [
        {
            "code": "IN", "name": "India", "flag": "🇮🇳",
            "cities": ["Bangalore", "Mumbai", "Hyderabad", "Pune", "Chennai", "Delhi", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "💼", "desc": "Professional network",    "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+India"},
                {"name": "Naukri",    "icon": "🔶", "desc": "India's #1 job portal",   "rating": 4.7, "color": "#fd7e00", "urlTemplate": "https://www.naukri.com/{skills}-jobs-in-{loc}"},
                {"name": "Indeed IN", "icon": "🔍", "desc": "Indian job search",       "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://in.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Shine",     "icon": "✨", "desc": "Leading Indian job board", "rating": 4.2, "color": "#00bfa5", "urlTemplate": "https://www.shine.com/job-search/{skills}-jobs-in-{loc}"},
                {"name": "Wellfound", "icon": "🚀", "desc": "Startup jobs India",       "rating": 4.3, "color": "#fb4a00", "urlTemplate": "https://wellfound.com/jobs?q={skills}&l=India"},
                {"name": "Instahyre", "icon": "⚡", "desc": "AI-powered hiring India",  "rating": 4.4, "color": "#7c4dff", "urlTemplate": "https://www.instahyre.com/search-jobs/?keywords={skills}&location={loc}"},
            ],
        },
        {
            "code": "SG", "name": "Singapore", "flag": "🇸🇬",
            "cities": ["Singapore", "Remote"],
            "boards": [
                {"name": "LinkedIn",        "icon": "💼", "desc": "Professional network",       "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location=Singapore"},
                {"name": "JobsDB",          "icon": "📱", "desc": "Asia's top job board",       "rating": 4.5, "color": "#e53935", "urlTemplate": "https://sg.jobsdb.com/j?q={skills}&l=Singapore"},
                {"name": "MyCareersFuture", "icon": "🇸🇬", "desc": "Singapore government jobs", "rating": 4.6, "color": "#d62b2b", "urlTemplate": "https://www.mycareersfuture.gov.sg/search?search={skills}"},
                {"name": "Indeed SG",       "icon": "🔍", "desc": "Singapore job search",       "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://sg.indeed.com/jobs?q={skills}&l=Singapore"},
            ],
        },
        {
            "code": "AU", "name": "Australia", "flag": "🇦🇺",
            "cities": ["Sydney", "Melbourne", "Brisbane", "Perth", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "💼", "desc": "Professional network",      "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Australia"},
                {"name": "Seek",      "icon": "🔎", "desc": "Australia's #1 job site",   "rating": 4.8, "color": "#e60278", "urlTemplate": "https://www.seek.com.au/{skills}-jobs/in-{loc}"},
                {"name": "Indeed AU", "icon": "🔍", "desc": "Australian job search",     "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://au.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Jora",      "icon": "🦘", "desc": "Australian job aggregator", "rating": 4.1, "color": "#ff6b35", "urlTemplate": "https://au.jora.com/j?q={skills}&l={loc}"},
            ],
        },
        {
            "code": "JP", "name": "Japan", "flag": "🇯🇵",
            "cities": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Remote"],
            "boards": [
                {"name": "LinkedIn",  "icon": "💼", "desc": "Professional network",  "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Japan"},
                {"name": "Gaijinpot", "icon": "🗾", "desc": "English jobs in Japan", "rating": 4.4, "color": "#e53935", "urlTemplate": "https://jobs.gaijinpot.com/index/index/search?language=1&keywords={skills}"},
                {"name": "Indeed JP", "icon": "🔍", "desc": "Japan job search",      "rating": 4.4, "color": "#003a9b", "urlTemplate": "https://jp.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
    ],
    "Middle East & Africa": [
        {
            "code": "AE", "name": "UAE", "flag": "🇦🇪",
            "cities": ["Dubai", "Abu Dhabi", "Sharjah", "Remote"],
            "boards": [
                {"name": "LinkedIn",   "icon": "💼", "desc": "Professional network",   "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+UAE"},
                {"name": "Bayt",       "icon": "🌙", "desc": "MENA's top job board",   "rating": 4.6, "color": "#00a651", "urlTemplate": "https://www.bayt.com/en/uae/jobs/{skills}-jobs/"},
                {"name": "GulfTalent", "icon": "🏆", "desc": "Gulf professional jobs", "rating": 4.4, "color": "#ff6b35", "urlTemplate": "https://www.gulftalent.com/jobs?search%5Bkeywords%5D={skills}"},
                {"name": "Indeed AE",  "icon": "🔍", "desc": "UAE job search",         "rating": 4.3, "color": "#003a9b", "urlTemplate": "https://ae.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
        {
            "code": "ZA", "name": "South Africa", "flag": "🇿🇦",
            "cities": ["Johannesburg", "Cape Town", "Durban", "Remote"],
            "boards": [
                {"name": "LinkedIn",       "icon": "💼", "desc": "Professional network",         "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+South+Africa"},
                {"name": "PNet",           "icon": "🌍", "desc": "South Africa's top job board", "rating": 4.5, "color": "#e53935", "urlTemplate": "https://www.pnet.co.za/jobs/{skills}-jobs/in-{loc}/"},
                {"name": "CareerJunction", "icon": "🔀", "desc": "SA career portal",             "rating": 4.3, "color": "#0072bc", "urlTemplate": "https://www.careerjunction.co.za/jobs/results?keywords={skills}"},
            ],
        },
    ],
    "Latin America": [
        {
            "code": "BR", "name": "Brazil", "flag": "🇧🇷",
            "cities": ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Remote"],
            "boards": [
                {"name": "LinkedIn", "icon": "💼", "desc": "Professional network",       "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Brazil"},
                {"name": "Catho",    "icon": "🐱", "desc": "Brazil's leading job board", "rating": 4.4, "color": "#e53935", "urlTemplate": "https://www.catho.com.br/vagas/{skills}/"},
                {"name": "Indeed BR","icon": "🔍", "desc": "Brazilian job search",       "rating": 4.3, "color": "#003a9b", "urlTemplate": "https://br.indeed.com/jobs?q={skills}&l={loc}"},
                {"name": "Gupy",     "icon": "🚀", "desc": "Brazilian HR tech platform", "rating": 4.5, "color": "#7c4dff", "urlTemplate": "https://portal.gupy.io/job-search?term={skills}"},
            ],
        },
        {
            "code": "MX", "name": "Mexico", "flag": "🇲🇽",
            "cities": ["Mexico City", "Guadalajara", "Monterrey", "Remote"],
            "boards": [
                {"name": "LinkedIn",    "icon": "💼", "desc": "Professional network",   "rating": 4.8, "color": "#0a66c2", "urlTemplate": "https://www.linkedin.com/jobs/search/?keywords={skills}&location={loc}%2C+Mexico"},
                {"name": "OCC Mundial", "icon": "🌎", "desc": "Mexico's top job board", "rating": 4.5, "color": "#d62b2b", "urlTemplate": "https://www.occ.com.mx/empleos/de-{skills}/en-{loc}/"},
                {"name": "Indeed MX",   "icon": "🔍", "desc": "Mexican job search",     "rating": 4.3, "color": "#003a9b", "urlTemplate": "https://mx.indeed.com/jobs?q={skills}&l={loc}"},
            ],
        },
    ],
}


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def ask_claude(system_prompt: str, user_message: str, max_tokens: int = 2000):
    """Call Claude and return parsed JSON (dict or list)."""
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
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


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Parse resume → detect skills, role, gaps, salary & generate job matches.

    Request  JSON: { resume, country, city }
    Response JSON: { skills, role, confidence, missing, salaryRef, jobs[] }
    """
    body    = request.get_json(force=True)
    resume  = (body.get("resume")  or "").strip()
    country = (body.get("country") or "").strip()
    city    = (body.get("city")    or "Any City").strip()

    if not resume:
        return jsonify({"error": "Resume text is required."}), 400
    if not country:
        return jsonify({"error": "Country is required."}), 400

    system = """You are an expert resume parser and job-matching AI.

Given a resume, a target country, and an optional preferred city:
1. Extract every technical and soft skill mentioned.
2. Infer the candidate's most likely job role/title.
3. Identify common skills required for that role that are MISSING from the resume.
4. Provide a realistic local salary range for that role in that country.
5. Generate 6-8 realistic, varied job listings matching the candidate's profile for that country/city.

Return ONLY valid JSON — no markdown fences, no prose — with exactly these top-level keys:

{
  "skills":     ["skill1", "skill2", ...],
  "role":       "Detected Role Title",
  "confidence": 85,
  "missing":    ["gap1", "gap2", ...],
  "salaryRef":  "Local salary range string",
  "jobs": [
    {
      "title":          "Job Title",
      "company":        "Company Name",
      "score":          0.87,
      "skillScore":     0.75,
      "companyRating":  4.2,
      "salary":         "Salary range string",
      "location":       "City, Country",
      "remote":         true,
      "experience":     "3-5 years",
      "requiredSkills": ["skill1", "skill2"],
      "matched":        ["skill1"],
      "missing":        ["skill2"],
      "niceToHave":     ["skill3"],
      "snippet":        "1-2 sentence job description.",
      "linkedinUrl":    "https://www.linkedin.com/jobs/search/?keywords=Job+Title&location=City",
      "indeedUrl":      "https://www.indeed.com/jobs?q=Job+Title&l=City",
      "googleJobsUrl":  "https://www.google.com/search?q=Job+Title+jobs+City&ibp=htl;jobs",
      "glassdoorUrl":   "https://www.glassdoor.com/Job/jobs.htm?sc.keyword=Job+Title",
      "wellfoundUrl":   "https://wellfound.com/jobs?q=Job+Title&l=City"
    }
  ]
}"""

    user = f"Resume:\n{resume}\n\nTarget country: {country}\nPreferred city: {city}"

    try:
        data = ask_claude(system, user, max_tokens=3000)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"AI returned invalid JSON: {e}"}), 500
    except anthropic.APIError as e:
        return jsonify({"error": f"Anthropic API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)


@app.route("/api/review", methods=["POST"])
def review():
    """
    Generate a personalised AI career-coach review for one job listing.

    Request  JSON: full job object from /api/analyze
    Response JSON: { review, prioritySkills[] }
    """
    job = request.get_json(force=True)

    system = """You are a friendly, expert career coach reviewing a job match for a candidate.

Given a job object (title, company, matched/missing skills, score, etc.) write:
- A concise, honest, encouraging 2-3 sentence personalised review explaining the fit.
- A list of 3-5 priority skills the candidate should develop for this specific role.

Return ONLY valid JSON — no markdown fences, no prose — with exactly these keys:

{
  "review":         "Your personalised review here...",
  "prioritySkills": ["skill1", "skill2", "skill3"]
}"""

    user = f"Job details:\n{json.dumps(job, indent=2)}"

    try:
        data = ask_claude(system, user, max_tokens=600)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"AI returned invalid JSON: {e}"}), 500
    except anthropic.APIError as e:
        return jsonify({"error": f"Anthropic API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(data)


@app.route("/api/roadmap", methods=["POST"])
def roadmap():
    """
    Generate a prioritised learning roadmap for missing skills.

    Request  JSON: { role, missingSkills[], userSkills[] }
    Response JSON: [ { skill, why, priority, weeks, resources[] } ]
    """
    body           = request.get_json(force=True)
    role           = (body.get("role") or "").strip()
    missing_skills = body.get("missingSkills") or []
    user_skills    = body.get("userSkills")    or []

    if not role or not missing_skills:
        return jsonify([])

    system = """You are a senior engineering mentor and career roadmap expert.

Given a target job role, skills the candidate is missing, and skills they already have:
- Produce a learning roadmap sorted by career impact (highest priority first).
- For each skill include: why it matters for this role, realistic weeks to learn it, and 2-3 real freely-accessible learning resources.

Return ONLY a valid JSON array — no markdown fences, no prose — where each element has exactly these keys:

[
  {
    "skill":     "Docker",
    "why":       "One-sentence explanation of why this skill matters for the target role.",
    "priority":  95,
    "weeks":     3,
    "resources": [
      { "name": "Docker Getting Started", "url": "https://docs.docker.com/get-started/",                  "platform": "Official Docs" },
      { "name": "Docker for Beginners",   "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo",           "platform": "YouTube"       }
    ]
  }
]"""

    user = (
        f"Target role: {role}\n"
        f"Skills to learn: {', '.join(missing_skills[:7])}\n"
        f"Skills already known: {', '.join(user_skills)}"
    )

    try:
        data = ask_claude(system, user, max_tokens=2500)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"AI returned invalid JSON: {e}"}), 500
    except anthropic.APIError as e:
        return jsonify({"error": f"Anthropic API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Ensure we always return a list
    if isinstance(data, dict):
        data = list(data.values())[0] if data else []

    return jsonify(data)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
