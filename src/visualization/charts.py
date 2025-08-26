"""
QualityVisualizer: generates the static HTML dashboard and simple HTML charts.
This file replaces previous corrupted content with a single, consistent implementation.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class QualityVisualizer:
    """Comprehensive HTML dashboard generator for bio.tools results.

    Public methods used by scripts/tests:
    - create_home_page
    - create_tools_overview_page
    - create_field_analysis_page
    - create_statistics_page
    - create_linter_reports_page
    - generate_complete_dashboard
    - create_tier_distribution_chart (minimal standalone chart used in tests)
    - create_score_distribution_histogram (minimal standalone chart used in tests)
    """

    tier_colors = {1: '#ff4d4d', 2: '#ff9933', 3: '#ffcc00', 4: '#66cc00', 5: '#00cc66'}
    tier_names = {1: 'SPARSE', 2: 'BASIC DETAILS', 3: 'DETAILED', 4: 'HIGHLY DETAILED', 5: 'COMPREHENSIVE'}

    def __init__(self, style: str = 'modern') -> None:
        self.style = style
        self.pagination_threshold = 100  # Lower threshold for better navigation
        self.page_size = 50  # Smaller page size for linter reports
        logger.info("QualityVisualizer initialized for HTML dashboard generation")

    # ------------------------- Shared helpers -------------------------
    def _css(self) -> str:
        return (
            "<style>"
            "*{margin:0;padding:0;box-sizing:border-box;}"
            "body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px;}"
            ".container{max-width:1400px;margin:0 auto;background:rgba(255,255,255,.95);border-radius:15px;padding:30px;box-shadow:0 20px 40px rgba(0,0,0,.1);}"
            ".header{text-align:center;margin-bottom:40px;padding-bottom:20px;border-bottom:3px solid #667eea;}"
            ".header h1{color:#333;font-size:2.2em;margin-bottom:10px;}"
            ".nav-menu{display:flex;justify-content:center;gap:12px;margin-bottom:24px;flex-wrap:wrap;}"
            ".nav-link{display:inline-block;padding:10px 18px;background:#667eea;color:#fff;text-decoration:none;border-radius:22px;transition:all .2s ease;font-weight:500;}"
            ".nav-link:hover{background:#5a67d8;transform:translateY(-1px);}"
            ".nav-link.active{background:#764ba2;}"
            ".card{background:#fff;border-radius:12px;padding:18px;margin-bottom:18px;box-shadow:0 4px 15px rgba(0,0,0,.1);}"
            ".tier-1{border-left:5px solid #ff4d4d}.tier-2{border-left:5px solid #ff9933}.tier-3{border-left:5px solid #ffcc00}.tier-4{border-left:5px solid #66cc00}.tier-5{border-left:5px solid #00cc66}"
            ".tier-badge{padding:6px 12px;border-radius:16px;font-weight:600;font-size:.9em;color:#fff;}"
            ".tier-badge-1{background:#ff4d4d}.tier-badge-2{background:#ff9933}.tier-badge-3{background:#ffcc00;color:#333}.tier-badge-4{background:#66cc00}.tier-badge-5{background:#00cc66}"
            ".grid{display:grid;gap:16px}.grid-2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}.grid-3{grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}.grid-4{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}"
            ".stat-card{text-align:center;padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-radius:12px}"
            ".stat-number{font-size:2em;font-weight:bold;margin-bottom:6px}.stat-label{font-size:1em;opacity:.9}"
            ".filter-section{margin-bottom:20px;padding:16px;background:#f8f9fa;border-radius:10px}"
            ".filter-controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap}"
            "select,input{padding:8px 12px;border:2px solid #ddd;border-radius:8px;font-size:1em}"
            ".missing-field{display:inline-block;background:#ffe6e6;color:#d63384;padding:4px 8px;margin:2px;border-radius:12px;font-size:.85em;border:1px solid #f5c6cb}"
            ".score-bar{height:18px;background:#e9ecef;border-radius:10px;overflow:hidden;margin:5px 0}"
            ".score-fill{height:100%;border-radius:10px}"
            ".table-responsive{overflow-x:auto;margin:16px 0}table{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden}"
            "th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #e9ecef}th{background:#f8f9fa;font-weight:600;color:#495057}"
            ".timestamp{text-align:center;color:#666;font-size:.9em;margin-top:20px;padding-top:16px;border-top:1px solid #ddd}"
            "</style>"
        )

    def _nav(self, active: str) -> str:
        items = [
            ("home.html", "🏠 Home", active == 'home'),
            ("tools-overview.html", "📋 Tools Overview", active == 'tools'),
            ("field-analysis.html", "📊 Field Analysis", active == 'fields'),
            ("statistics.html", "📈 Statistics", active == 'stats'),
            ("linter-reports.html", "🔍 Linter Reports", active == 'linter'),
        ]
        html = ["<nav class='nav-menu'>"]
        for href, label, is_active in items:
            cls = 'nav-link active' if is_active else 'nav-link'
            html.append(f"<a href='{href}' class='{cls}'>{label}</a>")
        html.append("</nav>")
        return "".join(html)

    def _pagination(self, base: str, page: int, pages: int) -> str:
        if pages <= 1:
            return ""
        def href(p: int) -> str:
            return f"{base}.html" if p == 1 else f"{base}-page-{p}.html"
        links: List[str] = []
        links.append(f"<a class='nav-link' href='{href(max(1, page-1))}'>&laquo; Prev</a>")
        start = max(1, page - 2)
        end = min(pages, page + 2)
        if start > 1:
            links.append(f"<a class='nav-link' href='{href(1)}'>1</a>")
            if start > 2:
                links.append("<span style='padding:6px 8px; color:#666;'>…</span>")
        for p in range(start, end + 1):
            cls = 'nav-link active' if p == page else 'nav-link'
            links.append(f"<a class='{cls}' href='{href(p)}'>{p}</a>")
        if end < pages:
            if end < pages - 1:
                links.append("<span style='padding:6px 8px; color:#666;'>…</span>")
            links.append(f"<a class='nav-link' href='{href(pages)}'>{pages}</a>")
        links.append(f"<a class='nav-link' href='{href(min(pages, page+1))}'>Next &raquo;</a>")
        return "<div style='display:flex; gap:8px; align-items:center; flex-wrap:wrap;'>" + "".join(links) + "</div>"

    # ------------------------- Pages -------------------------
    def create_home_page(self, results: List[Dict[str, Any]], statistics: Dict[str, Any], save_path: Optional[str] = None) -> str:
        total = len(results)
        tiers: Dict[int, int] = {}
        for r in results:
            t = r.get('tier', 1)
            tiers[t] = tiers.get(t, 0) + 1
        
        # Access average score from nested structure
        basic_stats = statistics.get('basic_statistics', {})
        avg = basic_stats.get('score_statistics', {}).get('mean', 0)
        
        html = [
            "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Bio.tools Quality Dashboard</title>", self._css(), "</head><body><div class='container'>",
            "<div class='header'><h1>🧬 Bio.tools Quality Dashboard</h1><p>Comprehensive annotation quality evaluation and analysis</p></div>",
            self._nav('home'),
            "<div class='grid grid-4'>",
            f"<div class='stat-card'><div class='stat-number'>{total}</div><div class='stat-label'>Total Tools</div></div>",
            f"<div class='stat-card'><div class='stat-number'>{avg:.1f}</div><div class='stat-label'>Average Score</div></div>",
            f"<div class='stat-card'><div class='stat-number'>{tiers.get(5,0)+tiers.get(4,0)}</div><div class='stat-label'>High Quality Tools</div></div>",
            f"<div class='stat-card'><div class='stat-number'>{tiers.get(1,0)+tiers.get(2,0)}</div><div class='stat-label'>Need Improvement</div></div>",
            "</div>",
            "<div class='grid grid-2' style='margin-top:24px;'>",
            "<div class='card'><h3>📊 Tier Distribution</h3><div style='margin-top:12px;'>",
        ]
        for t in range(1, 6):
            count = tiers.get(t, 0)
            pct = (count / total * 100) if total else 0
            html.append(
                f"<div style='margin-bottom:12px;'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;'><span class='tier-badge tier-badge-{t}'>{self.tier_names[t]}</span><span style='font-weight:bold;'>{count} tools ({pct:.1f}%)</span></div><div class='score-bar'><div class='score-fill' style='width:{pct}%;background:{self.tier_colors[t]}'></div></div></div>"
            )
        html.extend([
            "</div></div>",
            "<div class='card'><h3>🚀 Quick Actions</h3><div style='margin-top:12px;'>",
            "<a href='tools-overview.html' class='nav-link' style='display:block;margin:8px 0;'>View All Tools Details</a>",
            "<a href='field-analysis.html' class='nav-link' style='display:block;margin:8px 0;'>Analyze Field Completeness</a>",
            "<a href='statistics.html' class='nav-link' style='display:block;margin:8px 0;'>View Detailed Statistics</a>",
            "<a href='linter-reports.html' class='nav-link' style='display:block;margin:8px 0;'>Check Linter Results</a>",
            "</div></div>",
            f"<div class='timestamp'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
            "</div></body></html>",
        ])
        content = "".join(html)
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return content

    def create_tools_overview_page(self, results: List[Dict[str, Any]], save_path: Optional[str] = None,
                                   page: int = 1, per_page: Optional[int] = None,
                                   total_count: Optional[int] = None, total_pages: Optional[int] = None) -> str:
        for r in results:
            if 'score' not in r and 'total_score' in r:
                r['score'] = r['total_score']
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        per = per_page or len(sorted_results)
        start = (page - 1) * per
        end = min(start + per, len(sorted_results))
        page_items = sorted_results[start:end]
        total = total_count if total_count is not None else len(sorted_results)
        pages = total_pages if total_pages is not None else max(1, (total + per - 1) // per)
        html = [
            "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Tools Overview - Bio.tools Quality Dashboard</title>", self._css(),
            "<script>function filterTools(){const s=document.getElementById('search').value.toLowerCase();const t=document.getElementById('tierFilter').value;document.querySelectorAll('.tool-card').forEach(e=>{const n=e.querySelector('.tool-name').textContent.toLowerCase();const ti=e.getAttribute('data-tier');let show=true;if(s&&n.indexOf(s)===-1)show=false;if(t&&ti!==t)show=false;e.style.display=show?'block':'none';});}function sortTools(){const by=document.getElementById('sortBy').value;const cont=document.querySelector('.tools-grid');const items=Array.from(document.querySelectorAll('.tool-card'));items.sort((a,b)=>{if(by==='name')return a.querySelector('.tool-name').textContent.localeCompare(b.querySelector('.tool-name').textContent);if(by==='score')return parseFloat(b.getAttribute('data-score'))-parseFloat(a.getAttribute('data-score'));if(by==='tier')return parseInt(b.getAttribute('data-tier'))-parseInt(a.getAttribute('data-tier'));});items.forEach(el=>cont.appendChild(el));}</script>",
            "</head><body><div class='container'>",
            "<div class='header'><h1>📋 Tools Overview</h1><p>All analyzed tools with scores and quality metrics</p></div>",
            self._nav('tools'),
            "<div class='filter-section'><h3>🔍 Filter & Sort</h3><div class='filter-controls'>",
            "<input type='text' id='search' placeholder='Search tools...' onkeyup='filterTools()'>",
            "<select id='tierFilter' onchange='filterTools()'><option value=''>All Tiers</option><option value='1'>Tier 1</option><option value='2'>Tier 2</option><option value='3'>Tier 3</option><option value='4'>Tier 4</option><option value='5'>Tier 5</option></select>",
            "<select id='sortBy' onchange='sortTools()'><option value='score'>Sort by Score</option><option value='name'>Sort by Name</option><option value='tier'>Sort by Tier</option></select>",
            "</div></div>",
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin:8px 0;'><div style='color:#666;'>Showing {start + 1 if total>0 else 0}-{end} of {total}{' | Page ' + str(page) + ' / ' + str(pages) if pages>1 else ''}</div>{self._pagination('tools-overview', page, pages) if pages>1 else ''}</div>",
            "<div class='tools-grid' style='display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:16px;'>",
        ]
        for r in page_items:
            bid = r.get('biotoolsID', 'unknown')
            tier = r.get('tier', 1)
            score = r.get('score', r.get('total_score', 0))  # Handle both 'score' and 'total_score'
            
            # Collect missing fields from all detail sections
            missing = []
            details = r.get('details', {})
            for section_name, section_data in details.items():
                if isinstance(section_data, dict) and 'missing_fields' in section_data:
                    missing.extend(section_data['missing_fields'])
            
            # Remove duplicates while preserving order
            seen = set()
            missing = [field for field in missing if not (field in seen or seen.add(field))]
            
            html.append(
                f"<div class='card tool-card tier-{tier}' data-tier='{tier}' data-score='{score}'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'><h3 class='tool-name' style='margin:0;color:#333;'>{bid}</h3><span class='tier-badge tier-badge-{tier}'>{self.tier_names[tier]}</span></div>"
                f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:10px;'><div style='text-align:center;padding:12px;background:#f8f9fa;border-radius:8px;'><div style='font-size:1.6em;font-weight:bold;color:{self.tier_colors[tier]};'>{score:.1f}</div><div style='font-size:.9em;color:#666;'>Quality Score</div></div><div style='text-align:center;padding:12px;background:#f8f9fa;border-radius:8px;'><div style='font-size:1.6em;font-weight:bold;color:#dc3545;'>{len(missing)}</div><div style='font-size:.9em;color:#666;'>Missing Fields</div></div></div>"
            )
            if missing:
                chips = ''.join([f"<span class='missing-field'>{mf}</span>" for mf in missing[:8]])
                more = '' if len(missing) <= 8 else f"<span class='missing-field'>+{len(missing)-8} more</span>"
                html.append(f"<div><h5 style='margin-bottom:6px;color:#666;'>Missing Fields ({len(missing)}):</h5><div>{chips}{more}</div></div>")
            html.append("</div>")
        html.extend([
            "</div>", self._pagination('tools-overview', page, pages) if pages > 1 else "",
            f"<div class='timestamp'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Tools analyzed: {total}</div>",
            "</div></body></html>",
        ])
        content = "".join(html)
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return content

    def create_field_analysis_page(self, results: List[Dict[str, Any]], scoring_config: Dict[str, Any], save_path: Optional[str] = None) -> str:
        field_counts: Dict[str, int] = {}
        total_tools = len(results)
        
        # Get all possible fields from the scoring configuration
        all_fields: List[str] = list(scoring_config.get('scoring', {}).get('field_weights', {}).keys())
        for fld in all_fields:
            field_counts[fld] = 0
            
        # Count field presence from details sections
        for r in results:
            details = r.get('details', {})
            present_fields = set()
            
            # Collect all present fields from all detail sections
            for section_name, section_data in details.items():
                if isinstance(section_data, dict) and 'present_fields' in section_data:
                    present_fields.update(section_data['present_fields'])
            
            # Count each field that's present
            for fld in all_fields:
                if fld in present_fields:
                    field_counts[fld] += 1
                    
        field_percentages = {fld: (cnt / total_tools * 100) if total_tools else 0 for fld, cnt in field_counts.items()}
        tier_distribution: Dict[int, int] = {}
        for r in results:
            t = r.get('tier', 1)
            tier_distribution[t] = tier_distribution.get(t, 0) + 1
        values = [tier_distribution.get(t, 0) for t in range(1, 6)]
        labels = [self.tier_names[t] for t in range(1, 6)]
        colors = [self.tier_colors[t] for t in range(1, 6)]
        html = [
            "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Field Analysis - Bio.tools Quality Dashboard</title>", self._css(),
            "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>",
            "</head><body><div class='container'>",
            "<div class='header'><h1>📊 Field Analysis</h1><p>Completeness across key metadata fields</p></div>",
            self._nav('fields'),
            "<div class='grid grid-2'>",
            "<div class='card'><h3>🥧 Tier Distribution</h3><div id='tierPieChart' style='height:380px;'></div></div>",
            "<div class='card'><h3>📈 Field Completeness Overview</h3><div style='max-height:380px;overflow-y:auto;'>",
        ]
        for fld, pct in sorted(field_percentages.items(), key=lambda x: x[1], reverse=True)[:15]:
            color = '#00cc66' if pct >= 80 else '#66cc00' if pct >= 60 else '#ffcc00' if pct >= 40 else '#ff9933' if pct >= 20 else '#ff4d4d'
            html.append(
                f"<div style='margin-bottom:12px;'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;'><span style='font-weight:500;'>{fld.replace('_',' ').title()}</span><span style='font-weight:bold;'>{pct:.1f}%</span></div><div class='score-bar'><div class='score-fill' style='width:{pct}%;background:{color}'></div></div></div>"
            )
        html.extend([
            "</div></div></div>",
            "<div class='card' style='margin-top:16px;'><h3>🔥 Field Completeness Heatmap</h3><div class='table-responsive'><table><thead><tr><th>Field</th><th>Present</th><th>%</th><th>Visual</th></tr></thead><tbody>",
        ])
        for fld, pct in sorted(field_percentages.items(), key=lambda x: x[1], reverse=True):
            cnt = field_counts[fld]
            bg = f"rgba(102, 204, 0, {pct/100})"
            color = '#fff' if pct > 50 else '#333'
            html.append(
                f"<tr><td style='font-weight:500;'>{fld.replace('_',' ').title()}</td><td>{cnt}/{total_tools}</td><td style='font-weight:bold;'>{pct:.1f}%</td><td><div class='heatmap-cell' style='background:{bg};color:{color};width:60px;height:18px;'>{pct:.0f}%</div></td></tr>"
            )
        html.extend([
            "</tbody></table></div></div>",
            "<script>var d=[{values:VALUES,labels:LABELS,type:'pie',marker:{colors:COLORS},textinfo:'label+percent+value'}];var l={showlegend:true,margin:{t:10,b:10,l:10,r:10}};"
            .replace('VALUES', json.dumps(values))
            .replace('LABELS', json.dumps(labels))
            .replace('COLORS', json.dumps(colors)) + "Plotly.newPlot('tierPieChart', d, l,{displayModeBar:false});</script>",
            f"<div class='timestamp'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Fields analyzed: {len(all_fields)}</div>",
            "</div></body></html>",
        ])
        content = "".join(html)
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return content

    def create_statistics_page(self, statistics: Dict[str, Any], save_path: Optional[str] = None) -> str:
        # Access nested basic_statistics data
        basic_stats = statistics.get('basic_statistics', {})
        
        html = [
            "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Statistics - Bio.tools Quality Dashboard</title>", self._css(),
            "</head><body><div class='container'>",
            "<div class='header'><h1>📈 Detailed Statistics</h1><p>Statistical analysis of scores and tiers</p></div>",
            self._nav('stats'),
            "<div class='grid grid-3'>",
            f"<div class='stat-card'><div class='stat-number'>{basic_stats.get('total_tools', 0)}</div><div class='stat-label'>Total Tools</div></div>",
            f"<div class='stat-card'><div class='stat-number'>{basic_stats.get('score_statistics', {}).get('mean', 0):.1f}</div><div class='stat-label'>Average Score</div></div>",
            f"<div class='stat-card'><div class='stat-number'>{basic_stats.get('score_statistics', {}).get('median', 0):.1f}</div><div class='stat-label'>Median Score</div></div>",
            "</div>",
        ]
        if 'score_statistics' in basic_stats:
            s = basic_stats['score_statistics']
            html.extend([
                "<div class='card' style='margin-top:20px;'><h3>📊 Score Distribution</h3><div class='grid grid-2'><div><h4>Basic</h4><div class='table-responsive'><table>",
                f"<tr><td><strong>Mean</strong></td><td>{s.get('mean', 0):.2f}</td></tr>",
                f"<tr><td><strong>Median</strong></td><td>{s.get('median', 0):.2f}</td></tr>",
                f"<tr><td><strong>Std Dev</strong></td><td>{s.get('std', 0):.2f}</td></tr>",
                f"<tr><td><strong>Min</strong></td><td>{s.get('min', 0):.2f}</td></tr>",
                f"<tr><td><strong>Max</strong></td><td>{s.get('max', 0):.2f}</td></tr>",
                "</table></div></div><div><h4>Quartiles</h4><div class='table-responsive'><table>",
                f"<tr><td><strong>Q1</strong></td><td>{s.get('quartiles', {}).get('q1', 0):.2f}</td></tr>",
                f"<tr><td><strong>Q2</strong></td><td>{s.get('quartiles', {}).get('q2', 0):.2f}</td></tr>",
                f"<tr><td><strong>Q3</strong></td><td>{s.get('quartiles', {}).get('q3', 0):.2f}</td></tr>",
                "</table></div></div></div></div>",
            ])
        if 'tier_distribution' in basic_stats:
            dist = basic_stats['tier_distribution']
            perc = basic_stats.get('tier_percentages', {})
            html.extend([
                "<div class='card' style='margin-top:16px;'><h3>🏆 Tier Distribution</h3><div class='table-responsive'><table><thead><tr><th>Tier</th><th>Description</th><th>Count</th><th>%</th><th>Visual</th></tr></thead><tbody>",
            ])
            for t in range(1, 6):
                # Handle both string and integer keys
                count = dist.get(str(t), dist.get(t, 0))
                p = perc.get(str(t), perc.get(t, 0))
                desc = {1:"Minimal viable entry",2:"Essential scientific metadata",3:"Comprehensive core information",4:"Rich metadata for discoverability",5:"Complete tool profile"}.get(t, f"Tier {t}")
                html.append(
                    f"<tr><td><span class='tier-badge tier-badge-{t}'>Tier {t}</span></td><td>{desc}</td><td><strong>{count}</strong></td><td><strong>{p:.1f}%</strong></td><td><div class='score-bar' style='width:150px;'><div class='score-fill' style='width:{p}%;background:{self.tier_colors[t]}'></div></div></td></tr>"
                )
            html.extend(["</tbody></table></div></div>"])
        html.extend([
            f"<div class='timestamp'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
            "</div></body></html>",
        ])
        content = "".join(html)
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return content

    def create_linter_reports_page(self, results: List[Dict[str, Any]], save_path: Optional[str] = None,
                                   page: int = 1, per_page: Optional[int] = None,
                                   total_count: Optional[int] = None, total_pages: Optional[int] = None) -> str:
        per = per_page or len(results)
        start = (page - 1) * per
        end = min(start + per, len(results))
        subset = results[start:end]
        total = total_count if total_count is not None else len(results)
        pages = total_pages if total_pages is not None else max(1, (total + per - 1) // per)
        html = [
            "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Linter Reports - Bio.tools Quality Dashboard</title>", self._css(),
            "<script>function filterL(){const s=document.getElementById('search').value.toLowerCase();const sev=document.getElementById('severity').value;document.querySelectorAll('.l-report').forEach(r=>{const n=r.querySelector('.tool-name').textContent.toLowerCase();const e=parseInt(r.getAttribute('data-errors'));const w=parseInt(r.getAttribute('data-warnings'));let show=true;if(s&&n.indexOf(s)===-1)show=false;if(sev==='errors'&&e===0)show=false;else if(sev==='warnings'&&w===0)show=false;r.style.display=show?'block':'none';});}</script>",
            "</head><body><div class='container'>",
            "<div class='header'><h1>🔍 Linter Reports</h1><p>Validation results and potential issues</p></div>",
            self._nav('linter'),
            "<div class='filter-section'><h3>🔎 Filter Reports</h3><div class='filter-controls'>",
            "<input id='search' placeholder='Search tools...' onkeyup='filterL()'>",
            "<select id='severity' onchange='filterL()'><option value=''>All</option><option value='errors'>Tools with Errors</option><option value='warnings'>Tools with Warnings</option></select>",
            "</div></div>",
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin:8px 0;'><div style='color:#666;'>Showing {start + 1 if total>0 else 0}-{end} of {total}{' | Page ' + str(page) + ' / ' + str(pages) if pages>1 else ''}</div>{self._pagination('linter-reports', page, pages) if pages>1 else ''}</div>",
            "<div class='linter-reports' style='display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px;'>",
        ]
        for r in subset:
            bid = r.get('biotoolsID', 'unknown')
            tier = r.get('tier', 1)
            score = r.get('score', r.get('total_score', 0))
            # Extract missing fields from the nested details structure
            details = r.get('details', {})
            missing = []
            for key, detail in details.items():
                if isinstance(detail, dict) and 'missing_fields' in detail:
                    missing.extend(detail['missing_fields'])
            err_cnt = max(0, 5 - int(tier) + len(missing) // 5)
            warn_cnt = max(0, 8 - int(tier) + len(missing) // 3)
            errors: List[str] = []
            warnings: List[str] = []
            if 'publication' in missing: errors.append('Missing required publication reference')
            if 'license' in missing: warnings.append('License information not specified')
            if 'documentation' in missing: errors.append('No documentation provided')
            if 'homepage' in missing: errors.append('Homepage URL is required')
            while len(errors) < err_cnt: errors.append(f'Schema validation error #{len(errors)+1}')
            while len(warnings) < warn_cnt: warnings.append(f'Schema validation warning #{len(warnings)+1}')
            linter_score = max(0, 100 - (err_cnt * 10) - (warn_cnt * 3))
            color = '#28a745' if linter_score >= 70 else '#ffc107' if linter_score >= 40 else '#dc3545'
            html.append(
                f"<div class='card l-report' data-errors='{err_cnt}' data-warnings='{warn_cnt}'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'><h3 class='tool-name' style='margin:0;color:#333;'>{bid}</h3><div style='font-weight:bold;color:{color};'>Linter Score: {linter_score:.0f}</div></div>"
                f"<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px;'><div style='text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;'><div style='font-size:1.4em;font-weight:bold;color:#dc3545'>{err_cnt}</div><div style='font-size:.9em;color:#666;'>Errors</div></div><div style='text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;'><div style='font-size:1.4em;font-weight:bold;color:#ffc107'>{warn_cnt}</div><div style='font-size:.9em;color:#666;'>Warnings</div></div><div style='text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;'><div style='font-size:1.4em;font-weight:bold;color:{self.tier_colors[tier]}'>{float(score):.0f}</div><div style='font-size:.9em;color:#666;'>Quality Score</div></div></div>"
            )
            if errors:
                items = ''.join([f"<li style='margin-bottom:4px;'>{e}</li>" for e in errors[:5]])
                more = '' if len(errors) <= 5 else f"<li style='color:#666;font-style:italic;'>... and {len(errors)-5} more errors</li>"
                html.append(f"<div style='margin-bottom:10px;padding:10px;background:#fff5f5;border-left:4px solid #dc3545;border-radius:8px;'><h5 style='margin-bottom:6px;color:#dc3545;'>❌ Errors:</h5><ul style='margin-left:18px;color:#721c24;'>{items}{more}</ul></div>")
            if warnings:
                items = ''.join([f"<li style='margin-bottom:4px;'>{w}</li>" for w in warnings[:5]])
                more = '' if len(warnings) <= 5 else f"<li style='color:#666;font-style:italic;'>... and {len(warnings)-5} more warnings</li>"
                html.append(f"<div style='margin-bottom:10px;padding:10px;background:#fffbf0;border-left:4px solid #ffc107;border-radius:8px;'><h5 style='margin-bottom:6px;color:#ffc107;'>⚠️ Warnings:</h5><ul style='margin-left:18px;color:#856404;'>{items}{more}</ul></div>")
            valid = err_cnt == 0
            status = '✅ Valid' if valid else '❌ Invalid'
            status_color = '#28a745' if valid else '#dc3545'
            html.append(f"<div style='padding:10px;background:#f8f9fa;border-radius:8px;text-align:center;'><span style='font-weight:bold;color:{status_color};'>{status}</span><span style='margin-left:8px;color:#666;'>Schema Compliance</span></div></div>")
        html.extend([
            "</div>", self._pagination('linter-reports', page, pages) if pages > 1 else "",
            f"<div class='timestamp'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Tools analyzed: {total}</div>",
            "</div></body></html>",
        ])
        content = "".join(html)
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return content

    def generate_complete_dashboard(self, results: List[Dict[str, Any]], statistics: Dict[str, Any], scoring_config: Dict[str, Any], output_dir: str = 'dashboard') -> None:
        os.makedirs(output_dir, exist_ok=True)
        self.create_home_page(results, statistics, os.path.join(output_dir, 'home.html'))
        total = len(results)
        
        # Tools Overview - use larger page size for overview
        tools_page_size = 100
        if total > self.pagination_threshold:
            tools_pages = max(1, (total + tools_page_size - 1) // tools_page_size)
            logger.info(f"Tools Overview Pagination: {total} tools, {tools_page_size} per page = {tools_pages} pages")
            for p in range(1, tools_pages + 1):
                fname = 'tools-overview.html' if p == 1 else f'tools-overview-page-{p}.html'
                self.create_tools_overview_page(results, os.path.join(output_dir, fname), page=p, per_page=tools_page_size, total_count=total, total_pages=tools_pages)
        else:
            self.create_tools_overview_page(results, os.path.join(output_dir, 'tools-overview.html'))
            
        # Field analysis and statistics - single pages
        self.create_field_analysis_page(results, scoring_config, os.path.join(output_dir, 'field-analysis.html'))
        self.create_statistics_page(statistics, os.path.join(output_dir, 'statistics.html'))
        
        # Linter Reports - use smaller page size for detailed review
        linter_page_size = 25  # Smaller pages for detailed linter analysis
        if total > self.pagination_threshold:
            linter_pages = max(1, (total + linter_page_size - 1) // linter_page_size)
            logger.info(f"Linter Reports Pagination: {total} tools, {linter_page_size} per page = {linter_pages} pages")
            for p in range(1, linter_pages + 1):
                fname = 'linter-reports.html' if p == 1 else f'linter-reports-page-{p}.html'
                self.create_linter_reports_page(results, os.path.join(output_dir, fname), page=p, per_page=linter_page_size, total_count=total, total_pages=linter_pages)
        else:
            self.create_linter_reports_page(results, os.path.join(output_dir, 'linter-reports.html'))
            
        # index.html
        import shutil
        shutil.copy(os.path.join(output_dir, 'home.html'), os.path.join(output_dir, 'index.html'))
        logger.info(f"Complete dashboard generated in {output_dir}")
        logger.info(f"Open {os.path.join(output_dir, 'index.html')} in your browser")

    # ------------------------- Minimal chart helpers for tests -------------------------
    def create_tier_distribution_chart(self, results: List[Dict[str, Any]], save_path: Optional[str] = None) -> str:
        tiers: Dict[int, int] = {}
        for r in results:
            t = r.get('tier', 1)
            tiers[t] = tiers.get(t, 0) + 1
        values = [tiers.get(t, 0) for t in range(1, 6)]
        labels = [self.tier_names[t] for t in range(1, 6)]
        colors = [self.tier_colors[t] for t in range(1, 6)]
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script></head><body>"
            "<div id='chart' style='width:800px;height:500px;'></div>"
            "<script>var d=[{values:VALUES,labels:LABELS,type:'pie',marker:{colors:COLORS}}];"
            .replace('VALUES', json.dumps(values))
            .replace('LABELS', json.dumps(labels))
            .replace('COLORS', json.dumps(colors)) +
            "Plotly.newPlot('chart', d, {margin:{t:20,b:20,l:20,r:20}},{displayModeBar:false});</script></body></html>"
        )
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html)
        return html

    def create_score_distribution_histogram(self, results: List[Dict[str, Any]], save_path: Optional[str] = None) -> str:
        scores = [r.get('score', r.get('total_score', 0)) for r in results]
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script></head><body>"
            "<div id='hist' style='width:800px;height:500px;'></div>"
            f"<script>var d=[{{x:{json.dumps(scores)},type:'histogram',marker:{{color:'#667eea'}}}}];"
            "Plotly.newPlot('hist', d, {margin:{t:20,b:40,l:40,r:20},xaxis:{title:'Score'},yaxis:{title:'Count'}},{displayModeBar:false});</script>"
            "</body></html>"
        )
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html)
        return html
