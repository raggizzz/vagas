#!/usr/bin/env python3
"""
Gerador de Relatório Visual de Skills

Cria um relatório HTML interativo com as estatísticas de skills por setor.
"""

import pandas as pd
import json
from pathlib import Path

def generate_html_report():
    """Gera relatório HTML com as estatísticas"""
    
    # Carregar dados
    skills_df = pd.read_csv('skills_agg.csv')
    coverage_df = pd.read_csv('coverage_report.csv')
    
    # Calcular estatísticas gerais
    total_vagas = coverage_df['total_vagas'].sum()
    total_setores = len(coverage_df)
    total_skills = len(skills_df['skill'].unique())
    
    # Criar HTML básico
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Skills por Setor</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 30px; justify-content: center; }}
        .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; min-width: 150px; }}
        .summary-card h3 {{ margin: 0 0 10px 0; font-size: 2em; }}
        .summary-card p {{ margin: 0; opacity: 0.9; }}
        .sector-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .sector-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .sector-card h3 {{ color: #2980b9; margin-top: 0; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }}
        .skill-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ecf0f1; }}
        .skill-percentage {{ background: #3498db; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #34495e; color: white; }}
        tr:hover {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Skills por Setor</h1>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{total_vagas}</h3>
                <p>Total de Vagas</p>
            </div>
            <div class="summary-card">
                <h3>{total_setores}</h3>
                <p>Setores</p>
            </div>
            <div class="summary-card">
                <h3>{total_skills}</h3>
                <p>Skills Únicas</p>
            </div>
        </div>

        <h2>📈 Resumo por Setor</h2>
        <div class="sector-grid">
"""
    
    # Gerar cards dos setores
    for _, row in coverage_df.iterrows():
        html_content += f"""
            <div class="sector-card">
                <h3>{row['setor']}</h3>
                <p><strong>{row['total_vagas']}</strong> vagas • <strong>{row['skills_encontradas']}</strong> skills</p>
                <div style="margin-top: 10px;">
                    <strong>Top Skills:</strong><br>
                    {row['top3_skills'].replace(', ', '<br>')}
                </div>
            </div>
        """
    
    html_content += """
        </div>

        <h2>📋 Skills Detalhadas por Setor</h2>
        <table>
            <thead>
                <tr>
                    <th>Setor</th>
                    <th>Skill</th>
                    <th>Contagem</th>
                    <th>Total do Setor</th>
                    <th>Percentual</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Gerar tabela de skills
    for _, row in skills_df.iterrows():
        html_content += f"""
                <tr>
                    <td>{row['setor']}</td>
                    <td>{row['skill']}</td>
                    <td>{row['contagem']}</td>
                    <td>{row['total_setor']}</td>
                    <td><strong>{row['percentual']}</strong></td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
        
        <h2>📊 Top 10 Skills Mais Demandadas</h2>
        <table>
            <thead>
                <tr>
                    <th>Ranking</th>
                    <th>Skill</th>
                    <th>Total de Menções</th>
                    <th>Setores que Usam</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Calcular top skills globais
    skill_totals = skills_df.groupby('skill')['contagem'].sum().sort_values(ascending=False).head(10)
    skill_sectors = skills_df.groupby('skill')['setor'].apply(list).to_dict()
    
    for i, (skill, total) in enumerate(skill_totals.items(), 1):
        sectors = ', '.join(skill_sectors[skill][:3])  # Primeiros 3 setores
        if len(skill_sectors[skill]) > 3:
            sectors += f" (+{len(skill_sectors[skill])-3} outros)"
        
        html_content += f"""
                <tr>
                    <td><strong>#{i}</strong></td>
                    <td>{skill}</td>
                    <td>{total}</td>
                    <td>{sectors}</td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
    """
    
    # Salvar arquivo
    with open('relatorio_skills.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Relatório HTML gerado: relatorio_skills.html")
    print(f"📊 Estatísticas:")
    print(f"   • {total_vagas} vagas analisadas")
    print(f"   • {total_setores} setores identificados")
    print(f"   • {total_skills} skills únicas mapeadas")
    
    # Mostrar top 5 skills
    print(f"\n🏆 Top 5 Skills Mais Demandadas:")
    skill_totals = skills_df.groupby('skill')['contagem'].sum().sort_values(ascending=False).head(5)
    for i, (skill, total) in enumerate(skill_totals.items(), 1):
        print(f"   {i}. {skill}: {total} menções")

if __name__ == '__main__':
    generate_html_report()