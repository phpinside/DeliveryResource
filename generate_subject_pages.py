#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path
from string import Template
from typing import Optional


CSV_FILE = Path("teachers_rows.csv")
UPDATE_DATE = "2026年7月4日"

SUBJECT_CONFIGS = {
    "MATH": {
        "output": Path("math-teachers.html"),
        "title": "华北交付中心 · 优秀数学师资团队",
        "subject_cn": "数学",
        "hero_char": "数",
        "score_field": "mathScore",
        "score_label": "高考数学",
        "score_cap": 150,
        "score_top": 150,
        "score_high": 147,
        "score_mid": 143,
        "high_score_threshold": 135,
        "high_score_label": "135分+高分教练",
        "exam_note_html": "",
        "filter_buttons": """
  <button class="filter-btn active" data-filter="all">全部</button>
  <button class="filter-btn" data-filter="150">满分150</button>
  <button class="filter-btn" data-filter="145+">145分+</button>
  <button class="filter-btn" data-filter="140+">140分+</button>
  <button class="filter-btn" data-filter="135+">135分+</button>
  <button class="filter-btn" data-filter="comp">有竞赛奖项</button>""",
        "hero_text": "精选已明确选择数学学科的伴学教练，覆盖小学、初中、高中数学基础巩固、应试提分与思维训练",
        "total_label": "在册数学教练",
    },
    "PHYSICS": {
        "output": Path("physics-teachers.html"),
        "title": "华北交付中心 · 优秀物理师资团队",
        "subject_cn": "物理",
        "hero_char": "物",
        "score_field": "physicsScore",
        "score_label": "高考物理",
        "score_cap": 110,
        "score_top": 110,
        "score_high": 100,
        "score_mid": 95,
        "high_score_threshold": 90,
        "high_score_label": "90分+高分教练",
        "exam_note_html": """
<div class="exam-note">
  <div class="exam-note-inner">
    <div class="exam-note-title">物理 / 化学成绩满分说明</div>
    <div class="exam-note-text">中国大部分省份实行“3+1+2”新高考模式。旧高考理科综合地区理综满分 300 分，其中物理 110 分、化学 100 分、生物 90 分；所有新高考地区（包括“3+3”和“3+1+2”），化学均为独立考试科目，卷面满分统一为 100 分。因此本页面物理成绩最高按 110 分显示，化学成绩最高按 100 分显示。</div>
  </div>
</div>""",
        "filter_buttons": """
  <button class="filter-btn active" data-filter="all">全部</button>
  <button class="filter-btn" data-filter="110">110分</button>
  <button class="filter-btn" data-filter="100+">100分+</button>
  <button class="filter-btn" data-filter="95+">95分+</button>
  <button class="filter-btn" data-filter="90+">90分+</button>
  <button class="filter-btn" data-filter="85+">85分+</button>
  <button class="filter-btn" data-filter="comp">有竞赛奖项</button>""",
        "hero_text": "精选已明确选择物理学科的伴学教练，覆盖初高中物理提分、建模与应试训练",
        "total_label": "在册物理教练",
    },
    "CHEMISTRY": {
        "output": Path("chemistry-teachers.html"),
        "title": "华北交付中心 · 优秀化学师资团队",
        "subject_cn": "化学",
        "hero_char": "化",
        "score_field": "chemistryScore",
        "score_label": "高考化学",
        "score_cap": 100,
        "score_top": 100,
        "score_high": 95,
        "score_mid": 90,
        "high_score_threshold": 90,
        "high_score_label": "90分+高分教练",
        "exam_note_html": """
<div class="exam-note">
  <div class="exam-note-inner">
    <div class="exam-note-title">物理 / 化学成绩满分说明</div>
    <div class="exam-note-text">中国大部分省份实行“3+1+2”新高考模式。旧高考理科综合地区理综满分 300 分，其中物理 110 分、化学 100 分、生物 90 分；所有新高考地区（包括“3+3”和“3+1+2”），化学均为独立考试科目，卷面满分统一为 100 分。因此本页面物理成绩最高按 110 分显示，化学成绩最高按 100 分显示。</div>
  </div>
</div>""",
        "filter_buttons": """
  <button class="filter-btn active" data-filter="all">全部</button>
  <button class="filter-btn" data-filter="100">100分</button>
  <button class="filter-btn" data-filter="95+">95分+</button>
  <button class="filter-btn" data-filter="90+">90分+</button>
  <button class="filter-btn" data-filter="85+">85分+</button>
  <button class="filter-btn" data-filter="comp">有竞赛奖项</button>""",
        "hero_text": "精选已明确选择化学学科的伴学教练，覆盖初高中化学基础巩固、实验理解与应试提分",
        "total_label": "在册化学教练",
    },
}

EMPTY_COMPETITION_VALUES = {
    "",
    "无",
    "暂无",
    "没有",
    "未参加",
    "无竞赛",
    "无奖项",
    "没有参加",
}


PAGE_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --ink: #0e1117;
    --ink-light: #3a3f4b;
    --ink-muted: #7a8093;
    --gold: #c89a3b;
    --gold-light: #e8c06a;
    --gold-pale: #fdf6e3;
    --red: #b84c3a;
    --bg: #f8f5f0;
    --white: #ffffff;
    --card-bg: #ffffff;
    --border: #e8e0d4;
    --shadow-hover: 0 12px 40px rgba(14,17,23,0.15);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Noto Sans SC', sans-serif;
    background: var(--bg);
    color: var(--ink);
    min-height: 100vh;
    overflow-x: hidden;
  }

  .hero {
    background: var(--ink);
    color: var(--white);
    padding: 80px 24px 72px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(200,154,59,0.18) 0%, transparent 70%);
  }
  .hero::after {
    content: '$hero_char';
    position: absolute;
    right: -40px;
    bottom: -60px;
    font-family: 'Noto Serif SC', serif;
    font-size: 320px;
    font-weight: 900;
    color: rgba(255,255,255,0.03);
    pointer-events: none;
    line-height: 1;
  }
  .hero-org {
    font-family: 'Noto Serif SC', serif;
    font-size: clamp(28px, 4vw, 42px);
    font-weight: 900;
    letter-spacing: 8px;
    color: #ffffff;
    margin-bottom: 20px;
    position: relative;
  }
  .hero-update {
    margin-top: 28px;
    font-size: 11px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 1.5px;
    position: relative;
  }

  .exam-note {
    max-width: 1280px;
    margin: 28px auto 0;
    padding: 0 24px;
  }
  .exam-note-inner {
    background: var(--white);
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    border-radius: 4px;
    padding: 18px 22px;
  }
  .exam-note-title {
    font-family: 'Noto Serif SC', serif;
    font-size: 16px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 8px;
  }
  .exam-note-text {
    font-size: 13px;
    color: var(--ink-light);
    line-height: 1.8;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(200,154,59,0.15);
    border: 1px solid rgba(200,154,59,0.4);
    color: var(--gold-light);
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    padding: 6px 18px;
    border-radius: 2px;
    margin-bottom: 28px;
    font-weight: 500;
    position: relative;
  }
  .hero h1 {
    font-family: 'Noto Serif SC', serif;
    font-size: clamp(36px, 5vw, 64px);
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -1px;
    margin-bottom: 20px;
    position: relative;
  }
  .hero h1 em {
    font-style: normal;
    color: var(--gold-light);
  }
  .hero p {
    color: rgba(255,255,255,0.6);
    font-size: 16px;
    max-width: 640px;
    margin: 0 auto 40px;
    line-height: 1.8;
    font-weight: 300;
    position: relative;
  }
  .hero-stats {
    display: flex;
    justify-content: center;
    gap: 56px;
    flex-wrap: wrap;
    position: relative;
  }
  .stat-item { text-align: center; }
  .stat-num {
    font-family: 'Noto Serif SC', serif;
    font-size: 42px;
    font-weight: 900;
    color: var(--gold-light);
    line-height: 1;
    margin-bottom: 6px;
  }
  .stat-label {
    font-size: 12px;
    color: rgba(255,255,255,0.5);
    letter-spacing: 1px;
  }

  .section-header {
    padding: 56px 24px 32px;
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 20px;
  }
  .section-header h2 {
    font-family: 'Noto Serif SC', serif;
    font-size: 22px;
    font-weight: 700;
    color: var(--ink);
    white-space: nowrap;
  }
  .section-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, var(--border), transparent);
  }
  .section-count {
    font-size: 13px;
    color: var(--ink-muted);
    white-space: nowrap;
  }

  .filter-bar {
    padding: 0 24px 24px;
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }
  .filter-label {
    font-size: 12px;
    color: var(--ink-muted);
    margin-right: 4px;
    font-weight: 500;
  }
  .filter-btn {
    padding: 6px 16px;
    border: 1px solid var(--border);
    background: var(--white);
    color: var(--ink-light);
    font-size: 13px;
    font-family: 'Noto Sans SC', sans-serif;
    border-radius: 20px;
    cursor: pointer;
    transition: all .2s;
  }
  .filter-btn:hover, .filter-btn.active {
    background: var(--ink);
    color: var(--white);
    border-color: var(--ink);
  }
  .search-input {
    margin-left: auto;
    padding: 7px 16px;
    border: 1px solid var(--border);
    border-radius: 20px;
    font-size: 13px;
    font-family: 'Noto Sans SC', sans-serif;
    outline: none;
    width: 200px;
    background: var(--white);
    transition: border-color .2s;
  }
  .search-input:focus { border-color: var(--gold); }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    padding: 0 24px 80px;
    max-width: 1280px;
    margin: 0 auto;
  }

  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
    transition: transform .25s ease, box-shadow .25s ease;
    cursor: default;
    animation: fadeUp .4s ease both;
  }
  .card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .card-top {
    padding: 24px 24px 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: flex-start;
    gap: 16px;
  }
  .avatar {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: var(--ink);
    color: var(--gold-light);
    font-family: 'Noto Serif SC', serif;
    font-size: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .card-info { flex: 1; min-width: 0; }
  .card-name {
    font-family: 'Noto Serif SC', serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 4px;
  }
  .card-school {
    font-size: 12px;
    color: var(--ink-muted);
    line-height: 1.5;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .score-badge {
    background: var(--ink);
    color: var(--gold-light);
    font-family: 'Noto Serif SC', serif;
    font-size: 20px;
    font-weight: 900;
    padding: 8px 12px;
    border-radius: 4px;
    text-align: center;
    line-height: 1;
    flex-shrink: 0;
    min-width: 62px;
  }
  .score-badge span {
    display: block;
    font-size: 10px;
    font-family: 'Noto Sans SC', sans-serif;
    color: rgba(255,255,255,0.4);
    margin-top: 3px;
    font-weight: 400;
    letter-spacing: 1px;
  }
  .score-top { background: #1a0a00; color: #ffd700; }
  .score-high { background: #0e1a00; color: #a8e060; }
  .score-mid { background: #001520; color: #60c8e8; }

  .card-body { padding: 16px 24px 20px; }

  .comp-tag {
    display: inline-block;
    background: var(--gold-pale);
    color: #7a5a10;
    border: 1px solid rgba(200,154,59,0.3);
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 2px;
    margin-bottom: 12px;
    font-weight: 500;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .exp-text {
    font-size: 13px;
    color: var(--ink-light);
    line-height: 1.7;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .exp-text::before {
    content: '▸ ';
    color: var(--gold);
    font-size: 11px;
  }

  footer {
    background: var(--ink);
    color: rgba(255,255,255,0.4);
    text-align: center;
    padding: 32px 24px;
    font-size: 12px;
    letter-spacing: 1px;
  }
  footer a {
    color: rgba(255,255,255,0.5);
    text-decoration: none;
    margin: 0 8px;
    transition: color .2s;
  }
  footer a:hover { color: var(--gold-light); }

  @media (max-width: 600px) {
    .hero { padding: 56px 20px 48px; }
    .hero-stats { gap: 32px; }
    .stat-num { font-size: 32px; }
    .grid { grid-template-columns: 1fr; padding: 0 16px 60px; }
    .search-input { width: 100%; margin-left: 0; margin-top: 8px; }
  }
</style>
</head>
<body>

<section class="hero">
  <div class="hero-org">华北交付中心</div>
  <div class="hero-badge">优质师资 · 精准提分</div>
  <h1>专业$subject_cn<em>伴学团队</em></h1>
  <p>$hero_text</p>
  <div class="hero-stats">
    <div class="stat-item">
      <div class="stat-num">$total_count</div>
      <div class="stat-label">$total_label</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">$high_count</div>
      <div class="stat-label">$high_score_label</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">$competition_count</div>
      <div class="stat-label">竞赛背景教练</div>
    </div>
  </div>
  <div class="hero-update">数据更新日期：$update_date</div>
</section>

$exam_note_html

<div class="section-header">
  <h2>全部$subject_cn教练</h2>
  <div class="section-line"></div>
  <div class="section-count" id="count-label">共 $total_count 位</div>
</div>

<div class="filter-bar">
  <span class="filter-label">$subject_cn成绩：</span>
$filter_buttons
  <input class="search-input" type="text" placeholder="搜索姓名 / 学校" id="searchInput">
</div>

<div class="grid" id="teacherGrid"></div>

<footer>
  <p>© 华北交付中心 · 专业 · 严谨 · 负责 · 数据更新日期 $update_date</p>
  <p style="margin-top: 8px; color: rgba(255,255,255,0.3);">
    <a href="index.html">返回首页</a>
    <span>|</span>
    <a href="math-teachers.html">数学师资</a>
  </p>
</footer>

<script id="teachers-data" type="application/json">$data_json</script>
<script>
const teachers = JSON.parse(document.getElementById('teachers-data').textContent);
const grid = document.getElementById('teacherGrid');
const countLabel = document.getElementById('count-label');
let currentFilter = 'all';
let currentSearch = '';

function getScoreClass(score) {
  if (score >= $score_top) return 'score-top';
  if (score >= $score_high) return 'score-high';
  if (score >= $score_mid) return 'score-mid';
  return '';
}

function getAvatarColor(name) {
  const colors = [
    ['#1a1a2e','#e8c06a'], ['#0d1b2a','#60c8e8'], ['#1a0a00','#ffd700'],
    ['#0a1628','#a8e060'], ['#1e0a1e','#f0a0d0'], ['#0a1e0a','#80e880'],
  ];
  let h = 0;
  for (const c of String(name || '教练')) h = (h * 31 + c.charCodeAt(0)) % colors.length;
  return colors[h];
}

function teacherDisplayName(name) {
  const text = String(name || '教练').trim();
  const surname = text === '宋老师' ? '宋' : text.charAt(0);
  return surname + '老师';
}

function shortText(value, maxLength) {
  const text = String(value || '');
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
}

function makeTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function renderCards(list) {
  grid.innerHTML = '';
  const fragment = document.createDocumentFragment();

  list.forEach((teacher, index) => {
    const [bg, fg] = getAvatarColor(teacher.name);
    const displayName = teacherDisplayName(teacher.name);

    const card = document.createElement('div');
    card.className = 'card';
    card.style.animationDelay = (index % 12 * 40) + 'ms';

    const cardTop = document.createElement('div');
    cardTop.className = 'card-top';

    const avatar = makeTextElement('div', 'avatar', displayName.charAt(0));
    avatar.style.background = bg;
    avatar.style.color = fg;

    const cardInfo = document.createElement('div');
    cardInfo.className = 'card-info';
    cardInfo.appendChild(makeTextElement('div', 'card-name', displayName));

    const school = makeTextElement('div', 'card-school', teacher.school);
    school.title = teacher.school;
    cardInfo.appendChild(school);

    const scoreBadge = makeTextElement('div', 'score-badge ' + getScoreClass(teacher.scoreValue), teacher.scoreLabel);
    scoreBadge.appendChild(makeTextElement('span', '', '$score_label'));

    cardTop.appendChild(avatar);
    cardTop.appendChild(cardInfo);
    cardTop.appendChild(scoreBadge);

    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';

    if (teacher.comp) {
      const compTag = makeTextElement('div', 'comp-tag', '奖项 ' + shortText(teacher.comp, 28));
      compTag.title = teacher.comp;
      cardBody.appendChild(compTag);
    }

    const expText = makeTextElement('div', 'exp-text', teacher.exp);
    expText.title = teacher.exp;
    cardBody.appendChild(expText);

    card.appendChild(cardTop);
    card.appendChild(cardBody);
    fragment.appendChild(card);
  });

  grid.appendChild(fragment);
  countLabel.textContent = '共 ' + list.length + ' 位';
}

function filteredTeachers() {
  const query = currentSearch.toLowerCase();

  return teachers.filter((teacher) => {
    const score = teacher.scoreValue;
    let show = true;

    if (currentFilter === '150') show = score === 150;
    else if (currentFilter === '145+') show = score >= 145;
    else if (currentFilter === '140+') show = score >= 140;
    else if (currentFilter === '135+') show = score >= 135;
    else if (currentFilter === '110') show = score === 110;
    else if (currentFilter === '100') show = score === 100;
    else if (currentFilter === '100+') show = score >= 100;
    else if (currentFilter === '95+') show = score >= 95;
    else if (currentFilter === '90+') show = score >= 90;
    else if (currentFilter === '85+') show = score >= 85;
    else if (currentFilter === 'comp') show = Boolean(teacher.comp);

    if (show && query) {
      const name = String(teacher.name || '').toLowerCase();
      const school = String(teacher.school || '').toLowerCase();
      show = name.includes(query) || school.includes(query);
    }

    return show;
  });
}

function applyFilters() {
  renderCards(filteredTeachers());
}

document.querySelectorAll('.filter-btn').forEach((button) => {
  button.addEventListener('click', function() {
    document.querySelectorAll('.filter-btn').forEach((item) => item.classList.remove('active'));
    this.classList.add('active');
    currentFilter = this.dataset.filter;
    applyFilters();
  });
});

document.getElementById('searchInput').addEventListener('input', function() {
  currentSearch = this.value.trim();
  applyFilters();
});

renderCards(teachers);
</script>
</body>
</html>
""")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def parse_subjects(value: str) -> list[str]:
    if not value:
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed]


def parse_score(value: str) -> Optional[float]:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def score_label(raw_value: str, numeric_value: Optional[float]) -> str:
    raw_text = clean_text(raw_value)
    if numeric_value is None:
        return raw_text or "待补充"
    if numeric_value.is_integer():
        return str(int(numeric_value))
    return f"{numeric_value:g}"


def has_competition(value: str) -> bool:
    text = clean_text(value).strip("。.;； ")
    return text not in EMPTY_COMPETITION_VALUES


def load_rows() -> list[dict[str, str]]:
    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def capped_score(value: Optional[float], score_cap: int) -> Optional[float]:
    if value is None:
        return None
    return min(value, float(score_cap))


def build_records(
    rows: list[dict[str, str]],
    subject_key: str,
    score_field: str,
    score_cap: int,
) -> list[dict[str, object]]:
    records = []

    for row in rows:
        subjects = parse_subjects(row.get("subjects", ""))
        if subject_key not in subjects:
            continue

        score_value = capped_score(parse_score(row.get(score_field, "")), score_cap)
        competition = clean_text(row.get("scienceCompetition", ""))
        experience = (
            clean_text(row.get("teachingExperience", ""))
            or clean_text(row.get("teachingStrengths", ""))
        )
        if len(experience) < 10:
            continue

        records.append({
            "name": clean_text(row.get("name", "")) or "教练",
            "school": clean_text(row.get("school", "")) or "学校信息待补充",
            "scoreLabel": score_label("", score_value),
            "scoreValue": score_value if score_value is not None else -1,
            "comp": competition if has_competition(competition) else "",
            "exp": experience,
            "_has_score": score_value is not None,
            "_score": score_value if score_value is not None else -1,
            "_updated_at": row.get("updatedAt", ""),
        })

    records.sort(
        key=lambda item: (item["_has_score"], item["_score"], item["_updated_at"]),
        reverse=True,
    )

    for record in records:
        del record["_has_score"]
        del record["_score"]
        del record["_updated_at"]

    return records


def render_page(config: dict[str, object], records: list[dict[str, object]]) -> str:
    data_json = json.dumps(records, ensure_ascii=False, indent=2).replace("</", "<\\/")
    high_count = sum(
        1 for record in records
        if float(record["scoreValue"]) >= int(config["high_score_threshold"])
    )
    competition_count = sum(1 for record in records if record["comp"])

    return PAGE_TEMPLATE.substitute(
        title=config["title"],
        hero_char=config["hero_char"],
        subject_cn=config["subject_cn"],
        hero_text=config["hero_text"],
        total_count=len(records),
        total_label=config["total_label"],
        high_count=high_count,
        high_score_label=config["high_score_label"],
        competition_count=competition_count,
        update_date=UPDATE_DATE,
        score_label=config["score_label"],
        score_top=config["score_top"],
        score_high=config["score_high"],
        score_mid=config["score_mid"],
        exam_note_html=config["exam_note_html"],
        filter_buttons=config["filter_buttons"],
        data_json=data_json,
    )


def main() -> None:
    rows = load_rows()

    for subject_key, config in SUBJECT_CONFIGS.items():
        records = build_records(rows, subject_key, config["score_field"], config["score_cap"])
        html = render_page(config, records)
        config["output"].write_text(html, encoding="utf-8")
        print(f"{subject_key}={len(records)} -> {config['output']}")


if __name__ == "__main__":
    main()
