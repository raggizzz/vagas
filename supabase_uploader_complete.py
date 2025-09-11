#!/usr/bin/env python3
"""
Script para upload dos dados estruturados completos para o Supabase
Baseado no arquivo vagas_todos_setores_estruturadas_completo.json
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class SupabaseUploaderComplete:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print(f"✅ Conectado ao Supabase: {self.supabase_url}")
    
    def clean_text(self, text: str) -> str:
        """Limpa e normaliza texto"""
        if not text or str(text).lower() in ['nan', 'null', 'none', '']:
            return None
        return str(text).strip()
    
    def clean_numeric(self, value: Any) -> Optional[float]:
        """Limpa e converte valores numéricos"""
        if value is None or str(value).lower() in ['nan', 'null', 'none', '']:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def clean_array(self, arr: List[str]) -> List[str]:
        """Limpa array removendo valores vazios ou nulos"""
        if not arr:
            return []
        return [self.clean_text(item) for item in arr if self.clean_text(item)]
    
    def extract_salary_from_text(self, salary_text: str) -> tuple:
        """Extrai valores de salário do texto"""
        if not salary_text or str(salary_text).lower() in ['nan', 'null', 'none']:
            return None, None
        
        import re
        # Buscar padrões de salário
        patterns = [
            r'R\$\s*([\d.,]+)\s*a\s*R\$\s*([\d.,]+)',
            r'([\d.,]+)\s*a\s*([\d.,]+)',
            r'R\$\s*([\d.,]+)',
            r'([\d.,]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(salary_text))
            if match:
                if len(match.groups()) == 2:
                    try:
                        min_val = float(match.group(1).replace('.', '').replace(',', '.'))
                        max_val = float(match.group(2).replace('.', '').replace(',', '.'))
                        return min_val, max_val
                    except:
                        continue
                else:
                    try:
                        val = float(match.group(1).replace('.', '').replace(',', '.'))
                        return val, val
                    except:
                        continue
        
        return None, None
    
    def insert_or_get_company(self, company_name: str, industry: str = None) -> int:
        """Insere ou busca empresa existente"""
        company_name = self.clean_text(company_name)
        if not company_name:
            return None
        
        # Buscar empresa existente
        result = self.supabase.table('companies').select('id').eq('name', company_name).execute()
        
        if result.data:
            return result.data[0]['id']
        
        # Inserir nova empresa
        company_data = {
            'name': company_name,
            'industry': self.clean_text(industry)
        }
        
        result = self.supabase.table('companies').insert(company_data).execute()
        return result.data[0]['id'] if result.data else None
    
    def map_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia dados do JSON para o formato do Supabase"""
        info_basicas = job_data.get('informacoes_basicas', {})
        localizacao = job_data.get('localizacao', {})
        remuneracao = job_data.get('remuneracao', {})
        jornada = job_data.get('jornada_trabalho', {})
        requisitos = job_data.get('requisitos', {})
        habilidades = job_data.get('habilidades_e_competencias', {})
        
        # Extrair salários
        salary_min, salary_max = self.extract_salary_from_text(
            remuneracao.get('texto_original', '')
        )
        
        # Se não extraiu do texto, usar valores diretos
        if salary_min is None:
            salary_min = self.clean_numeric(remuneracao.get('valor_minimo'))
        if salary_max is None:
            salary_max = self.clean_numeric(remuneracao.get('valor_maximo'))
        
        return {
            'external_id': str(job_data.get('id')),
            'title': self.clean_text(info_basicas.get('fonte')),
            'company_name': self.clean_text(info_basicas.get('empresa_principal')),
            'industry': self.clean_text(info_basicas.get('setor')),
            'area': self.clean_text(info_basicas.get('area')),
            'sector': self.clean_text(info_basicas.get('setor')),
            'modality': self.clean_text(jornada.get('modalidade')),
            'work_schedule': self.clean_text(jornada.get('jornada_extraida')),
            'location_city': self.clean_text(localizacao.get('cidade_extraida')),
            'location_state': self.clean_text(localizacao.get('estado_extraido')),
            'location_region': self.clean_text(localizacao.get('unidade')),
            'salary_min': salary_min,
            'salary_max': salary_max,
            'salary_currency': 'BRL',
            'salary_period': 'month',
            'education_level': self.clean_text(requisitos.get('formacao_minima')),
            'seniority': self.clean_text(requisitos.get('experiencia_necessaria')),
            'employment_type': self.clean_text(info_basicas.get('modalidade')),
            'source_name': 'Catho',
            'source_url': self.clean_text(info_basicas.get('link')),
            'raw_excerpt': self.clean_text(job_data.get('descricao_completa', {}).get('texto_completo')),
            'description': self.clean_text(job_data.get('descricao_completa', {}).get('texto_completo')),
            'published_date': self.clean_text(info_basicas.get('publicada_em')),
            'extraction_timestamp': datetime.now().isoformat(),
            'data_quality_score': 8.5,  # Score baseado na estruturação completa
            'pcd': False
        }
    
    def insert_job(self, job_data: Dict[str, Any]) -> Optional[int]:
        """Insere uma vaga no Supabase"""
        try:
            # Mapear dados
            mapped_data = self.map_job_data(job_data)
            
            # Processar empresa
            company_id = self.insert_or_get_company(
                mapped_data.get('company_name'),
                mapped_data.get('industry')
            )
            mapped_data['company_id'] = company_id
            
            # Remover campos None
            job_record = {k: v for k, v in mapped_data.items() if v is not None}
            
            # Inserir vaga principal
            result = self.supabase.table('jobs').insert(job_record).execute()
            
            if not result.data:
                print(f"❌ Erro ao inserir vaga: {mapped_data.get('title')}")
                return None
            
            job_id = result.data[0]['id']
            print(f"✅ Vaga inserida: {mapped_data.get('title')} (ID: {job_id})")
            
            # Inserir dados relacionados
            self.insert_job_responsibilities(job_id, job_data.get('responsabilidades', {}).get('lista_responsabilidades', []))
            self.insert_job_requirements_must(job_id, [job_data.get('requisitos', {}).get('requisitos_texto_original', '')])
            self.insert_job_tags(job_id, job_data.get('habilidades_e_competencias', {}).get('habilidades_tecnicas', []))
            
            # Inserir empresas mencionadas como tags
            empresas_mencionadas = job_data.get('informacoes_basicas', {}).get('empresas_mencionadas', [])
            if empresas_mencionadas:
                empresa_tags = [f"empresa:{emp}" for emp in empresas_mencionadas[:5]]  # Limitar a 5
                self.insert_job_tags(job_id, empresa_tags)
            
            return job_id
            
        except Exception as e:
            print(f"❌ Erro ao processar vaga {job_data.get('id', 'N/A')}: {str(e)}")
            return None
    
    def insert_job_responsibilities(self, job_id: int, responsibilities: List[str]):
        """Insere responsabilidades da vaga"""
        responsibilities = self.clean_array(responsibilities)
        if not responsibilities:
            return
        
        responsibility_records = [{'job_id': job_id, 'responsibility': resp} for resp in responsibilities]
        self.supabase.table('job_responsibilities').insert(responsibility_records).execute()
    
    def insert_job_requirements_must(self, job_id: int, requirements: List[str]):
        """Insere requisitos obrigatórios da vaga"""
        requirements = self.clean_array(requirements)
        if not requirements:
            return
        
        requirement_records = [{'job_id': job_id, 'requirement': req} for req in requirements]
        self.supabase.table('job_requirements_must').insert(requirement_records).execute()
    
    def insert_job_tags(self, job_id: int, tags: List[str]):
        """Insere tags da vaga"""
        tags = self.clean_array(tags)
        if not tags:
            return
        
        tag_records = [{'job_id': job_id, 'tag': tag} for tag in tags]
        self.supabase.table('job_tags').insert(tag_records).execute()
    
    def upload_from_json(self, json_file_path: str, batch_size: int = 10, max_records: int = None):
        """Faz upload de vagas a partir do arquivo JSON estruturado completo"""
        print(f"📁 Carregando dados de: {json_file_path}")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)
            
            if max_records:
                jobs_data = jobs_data[:max_records]
                print(f"📊 Limitando a {max_records} registros para teste")
            
            print(f"📊 Total de vagas a processar: {len(jobs_data)}")
            
            successful_uploads = 0
            failed_uploads = 0
            
            for i, job_data in enumerate(jobs_data, 1):
                title = job_data.get('informacoes_basicas', {}).get('fonte', 'N/A')
                print(f"\n[{i}/{len(jobs_data)}] Processando: {title}")
                
                job_id = self.insert_job(job_data)
                
                if job_id:
                    successful_uploads += 1
                else:
                    failed_uploads += 1
                
                # Pausa a cada batch para evitar rate limiting
                if i % batch_size == 0:
                    print(f"\n⏸️ Processados {i} registros. Pausando...")
                    import time
                    time.sleep(1)
            
            print(f"\n📈 Resumo do upload:")
            print(f"✅ Sucessos: {successful_uploads}")
            print(f"❌ Falhas: {failed_uploads}")
            print(f"📊 Total: {len(jobs_data)}")
            
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {json_file_path}")
        except json.JSONDecodeError:
            print(f"❌ Erro ao decodificar JSON: {json_file_path}")
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
    
    def upload_batch(self, jobs_data: List[dict]) -> int:
        """Faz upload de um lote de vagas"""
        successful_uploads = 0
        
        for job_data in jobs_data:
            try:
                job_id = self.insert_job(job_data)
                if job_id:
                    successful_uploads += 1
            except Exception as e:
                print(f"❌ Erro ao inserir vaga: {e}")
                continue
        
        return successful_uploads
    
    def get_upload_stats(self) -> dict:
        """Retorna estatísticas do upload"""
        try:
            # Total de vagas
            total_jobs = self.supabase.table('jobs').select('id', count='exact').execute()
            
            # Vagas por setor
            sectors = self.supabase.table('jobs').select('sector').execute()
            sector_counts = {}
            for job in sectors.data:
                sector = job.get('sector', 'N/A')
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            
            # Vagas por modalidade
            modalities = self.supabase.table('jobs').select('modality').execute()
            modality_counts = {}
            for job in modalities.data:
                mod = job.get('modality', 'N/A')
                modality_counts[mod] = modality_counts.get(mod, 0) + 1
            
            return {
                'total_jobs': total_jobs.count,
                'top_sectors': dict(sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
                'modalities': modality_counts
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {str(e)}")
            return {}
    
    def get_stats(self):
        """Obtém estatísticas das vagas no Supabase"""
        stats = self.get_upload_stats()
        
        if stats:
            print(f"📊 Total de vagas: {stats.get('total_jobs', 0)}")
            
            print(f"📊 Top 5 setores:")
            for sector, count in stats.get('top_sectors', {}).items():
                print(f"   {sector}: {count}")
            
            print(f"📊 Vagas por modalidade:")
            for mod, count in stats.get('modalities', {}).items():
                print(f"   {mod}: {count}")
        else:
            print("❌ Não foi possível obter estatísticas")

def main():
    """Função principal"""
    uploader = SupabaseUploaderComplete()
    
    # Arquivo JSON estruturado completo
    json_file = 'vagas_todos_setores_estruturadas_completo.json'
    
    if os.path.exists(json_file):
        print(f"🚀 Iniciando upload do arquivo: {json_file}")
        
        # Fazer upload de teste com 50 registros primeiro
        print("\n🧪 Fazendo upload de teste com 50 registros...")
        uploader.upload_from_json(json_file, batch_size=5, max_records=50)
        
        print(f"\n📊 Estatísticas após upload de teste:")
        uploader.get_stats()
        
        # Perguntar se deve continuar com todos os registros
        response = input("\n❓ Continuar com upload completo? (s/n): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            print("\n🚀 Iniciando upload completo...")
            uploader.upload_from_json(json_file, batch_size=10)
            
            print(f"\n📊 Estatísticas finais:")
            uploader.get_stats()
        else:
            print("\n✅ Upload de teste concluído.")
    else:
        print(f"❌ Arquivo não encontrado: {json_file}")
        print("📁 Arquivos disponíveis:")
        for file in os.listdir('.'):
            if file.endswith('.json'):
                print(f"   - {file}")

if __name__ == "__main__":
    main()