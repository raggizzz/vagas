#!/usr/bin/env python3
"""
Script para fazer upload de todas as vagas do JSON para o Supabase
Usa a biblioteca supabase-py para inserção em lotes
"""

import os
import json
from datetime import datetime, date
from decimal import Decimal
from supabase import create_client, Client
from dotenv import load_dotenv
import time
from typing import Dict, List, Any, Optional

class SupabaseVagasUploader:
    def __init__(self):
        load_dotenv()
        
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("❌ Variáveis SUPABASE_URL e SUPABASE_KEY não encontradas no .env")
        
        self.supabase: Client = create_client(self.url, self.key)
        self.stats = {
            'total_vagas': 0,
            'vagas_inseridas': 0,
            'empresas_inseridas': 0,
            'erros': 0,
            'inicio': datetime.now()
        }
        
        print(f"✅ Conectado ao Supabase: {self.url}")
    
    def clean_value(self, value: Any) -> Any:
        """Limpa e converte valores para tipos apropriados"""
        if value is None or value == "" or value == "null":
            return None
        
        if isinstance(value, str):
            value = value.strip()
            if value == "" or value.lower() == "null":
                return None
        
        return value
    
    def parse_salary(self, salary_str: str) -> tuple[Optional[float], Optional[float]]:
        """Extrai salário mínimo e máximo de uma string"""
        if not salary_str or salary_str.lower() in ['não informado', 'a combinar', 'null']:
            return None, None
        
        try:
            # Remove caracteres não numéricos exceto vírgulas, pontos e hífens
            import re
            clean_salary = re.sub(r'[^\d,.-]', '', salary_str)
            
            # Procura por padrões como "5000-8000" ou "5.000,00 - 8.000,00"
            if '-' in clean_salary or 'a' in salary_str.lower():
                parts = re.split(r'[-a]', clean_salary)
                if len(parts) >= 2:
                    min_sal = self.convert_to_float(parts[0].strip())
                    max_sal = self.convert_to_float(parts[1].strip())
                    return min_sal, max_sal
            
            # Se não tem range, usa como salário único
            single_salary = self.convert_to_float(clean_salary)
            return single_salary, single_salary
            
        except Exception:
            return None, None
    
    def convert_to_float(self, value: str) -> Optional[float]:
        """Converte string para float, lidando com formato brasileiro"""
        if not value:
            return None
        
        try:
            # Remove espaços e substitui vírgula por ponto
            clean_value = value.replace(' ', '').replace(',', '.')
            # Remove pontos que não são decimais (milhares)
            if clean_value.count('.') > 1:
                parts = clean_value.split('.')
                clean_value = ''.join(parts[:-1]) + '.' + parts[-1]
            
            return float(clean_value)
        except Exception:
            return None
    
    def insert_or_get_company(self, company_name: str, industry: str = None) -> Optional[int]:
        """Insere ou obtém ID da empresa"""
        if not company_name:
            return None
        
        try:
            # Primeiro tenta buscar a empresa
            result = self.supabase.table('companies').select('id').eq('name', company_name).execute()
            
            if result.data:
                return result.data[0]['id']
            
            # Se não existe, insere nova empresa
            company_data = {
                'name': company_name,
                'industry': self.clean_value(industry)
            }
            
            result = self.supabase.table('companies').insert(company_data).execute()
            
            if result.data:
                self.stats['empresas_inseridas'] += 1
                return result.data[0]['id']
            
        except Exception as e:
            print(f"⚠️  Erro ao inserir empresa '{company_name}': {e}")
        
        return None
    
    def prepare_job_data(self, vaga: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados da vaga para inserção"""
        # Extrair dados das seções estruturadas
        info_basicas = vaga.get('informacoes_basicas', {})
        localizacao = vaga.get('localizacao', {})
        remuneracao = vaga.get('remuneracao', {})
        jornada = vaga.get('jornada_trabalho', {})
        requisitos = vaga.get('requisitos', {})
        
        # Extrair salários
        salary_min, salary_max = None, None
        if remuneracao.get('valor_minimo'):
            salary_min = float(remuneracao['valor_minimo'])
        if remuneracao.get('valor_maximo'):
            salary_max = float(remuneracao['valor_maximo'])
        
        # Se não tem min/max, tenta extrair do texto original
        if not salary_min and not salary_max and remuneracao.get('texto_original'):
            salary_min, salary_max = self.parse_salary(str(remuneracao['texto_original']))
        
        # Função auxiliar para limpar e truncar strings
        def clean_and_truncate(value, max_length=None):
            cleaned = self.clean_value(value)
            if cleaned is None:
                return None
            if max_length and len(str(cleaned)) > max_length:
                return str(cleaned)[:max_length]
            return str(cleaned) if cleaned else None
        
        # Preparar dados principais da vaga
        job_data = {
            'title': clean_and_truncate(info_basicas.get('fonte', ''), 500),
            'company_name': clean_and_truncate(info_basicas.get('empresa_principal', ''), 255),
            'sector': clean_and_truncate(info_basicas.get('setor', ''), 100),
            'area': clean_and_truncate(info_basicas.get('area', ''), 100),
            'employment_type': clean_and_truncate(remuneracao.get('tipo', ''), 50),
            'work_schedule': clean_and_truncate(jornada.get('jornada_extraida', '')),
            'modality': clean_and_truncate(info_basicas.get('modalidade', ''), 50),
            'location_city': clean_and_truncate(localizacao.get('cidade_extraida', ''), 100),
            'location_state': clean_and_truncate(localizacao.get('estado_extraido', ''), 10),
            'location_region': clean_and_truncate(localizacao.get('localidade_original', ''), 100),
            'salary_min': salary_min,
            'salary_max': salary_max,
            'salary_currency': 'BRL',
            'salary_period': 'month',
            'education_level': clean_and_truncate(requisitos.get('formacao_minima', ''), 100),
            'seniority': clean_and_truncate(requisitos.get('experiencia_necessaria', ''), 100),
            'source_name': 'Catho',
            'source_url': clean_and_truncate(info_basicas.get('link', '')),
            'description': clean_and_truncate(requisitos.get('requisitos_texto_original', '')),
            'published_date': self.parse_date(info_basicas.get('publicada_em')),
            'extraction_timestamp': datetime.now().isoformat(),
            'data_quality_score': 0.8
        }
        
        # Remover campos None para não sobrescrever defaults
        return {k: v for k, v in job_data.items() if v is not None}
    
    def parse_date(self, date_str: Any) -> Optional[str]:
        """Converte string de data para formato ISO"""
        if not date_str:
            return None
        
        try:
            if isinstance(date_str, str):
                # Tenta vários formatos de data
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        return parsed_date.date().isoformat()
                    except ValueError:
                        continue
            return None
        except Exception:
            return None
    
    def insert_related_data(self, job_id: int, vaga: Dict[str, Any]):
        """Insere dados relacionados (benefícios, responsabilidades, etc.)"""
        try:
            responsabilidades = vaga.get('responsabilidades', {})
            requisitos = vaga.get('requisitos', {})
            info_basicas = vaga.get('informacoes_basicas', {})
            
            # Responsabilidades
            if 'lista_responsabilidades' in responsabilidades and isinstance(responsabilidades['lista_responsabilidades'], list):
                resp_data = []
                for resp in responsabilidades['lista_responsabilidades']:
                    if resp and str(resp).strip():
                        resp_data.append({
                            'job_id': job_id,
                            'responsibility': str(resp).strip()
                        })
                
                if resp_data:
                    self.supabase.table('job_responsibilities').insert(resp_data).execute()
            
            # Idiomas como requisitos
            if 'idiomas' in requisitos and isinstance(requisitos['idiomas'], list):
                req_data = []
                for idioma in requisitos['idiomas']:
                    if idioma and str(idioma).strip():
                        req_data.append({
                            'job_id': job_id,
                            'requirement': f"Idioma: {str(idioma).strip()}"
                        })
                
                if req_data:
                    self.supabase.table('job_requirements_must').insert(req_data).execute()
            
            # Empresas mencionadas como tags
            if 'empresas_mencionadas' in info_basicas and isinstance(info_basicas['empresas_mencionadas'], list):
                tags_data = []
                for empresa in info_basicas['empresas_mencionadas']:
                    if empresa and str(empresa).strip() and str(empresa).strip() != info_basicas.get('empresa_principal', ''):
                        tags_data.append({
                            'job_id': job_id,
                            'tag': str(empresa).strip()[:100]
                        })
                
                if tags_data:
                    self.supabase.table('job_tags').insert(tags_data).execute()
        
        except Exception as e:
            print(f"⚠️  Erro ao inserir dados relacionados para vaga {job_id}: {e}")
    
    def upload_batch(self, vagas: List[Dict[str, Any]], batch_size: int = 50) -> int:
        """Faz upload de um lote de vagas"""
        uploaded_count = 0
        
        for i in range(0, len(vagas), batch_size):
            batch = vagas[i:i + batch_size]
            
            print(f"📤 Processando lote {i//batch_size + 1} ({len(batch)} vagas)...")
            
            for idx, vaga in enumerate(batch):
                try:
                    if not isinstance(vaga, dict):
                        print(f"❌ Vaga {idx + 1} não é um dicionário")
                        self.stats['erros'] += 1
                        continue
                    
                    # Preparar dados da vaga
                    job_data = self.prepare_job_data(vaga)
                    
                    if not job_data.get('title') or not job_data.get('company_name'):
                        print(f"⚠️  Vaga {idx + 1} ignorada: título ou empresa em branco")
                        continue
                    
                    # Inserir ou obter empresa
                    company_id = self.insert_or_get_company(
                        job_data['company_name'], 
                        job_data.get('industry')
                    )
                    
                    if company_id:
                        job_data['company_id'] = company_id
                    
                    # Inserir vaga
                    result = self.supabase.table('jobs').insert(job_data).execute()
                    
                    if result.data:
                        job_id = result.data[0]['id']
                        
                        # Inserir dados relacionados
                        self.insert_related_data(job_id, vaga)
                        
                        uploaded_count += 1
                        self.stats['vagas_inseridas'] += 1
                        
                        if uploaded_count % 25 == 0:
                            print(f"✅ {uploaded_count} vagas processadas...")
                    
                except Exception as e:
                    self.stats['erros'] += 1
                    print(f"❌ Erro ao processar vaga {idx + 1}: {str(e)[:100]}...")
                    continue
            
            # Pequena pausa entre lotes
            time.sleep(0.5)
        
        return uploaded_count
    
    def load_and_upload_json(self, json_file: str):
        """Carrega JSON e faz upload de todas as vagas"""
        print(f"📂 Carregando dados de {json_file}...")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extrair lista de vagas do JSON
            if isinstance(data, dict):
                if 'vagas' in data:
                    vagas = data['vagas']
                elif 'jobs' in data:
                    vagas = data['jobs']
                else:
                    # Assumir que o dict inteiro são as vagas
                    vagas = list(data.values()) if all(isinstance(v, dict) for v in data.values()) else [data]
            elif isinstance(data, list):
                vagas = data
            else:
                raise ValueError("Formato de JSON não reconhecido")
            
            self.stats['total_vagas'] = len(vagas)
            print(f"📊 Total de vagas encontradas: {self.stats['total_vagas']}")
            
            if self.stats['total_vagas'] == 0:
                print("❌ Nenhuma vaga encontrada no arquivo JSON")
                return
            
            # Confirmar upload
            print(f"\n🚀 Iniciando upload de {self.stats['total_vagas']} vagas para o Supabase...")
            
            # Fazer upload em lotes
            uploaded = self.upload_batch(vagas)
            
            # Estatísticas finais
            self.print_final_stats()
            
        except FileNotFoundError:
            print(f"❌ Arquivo {json_file} não encontrado")
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(f"❌ Erro durante upload: {e}")
    
    def print_final_stats(self):
        """Imprime estatísticas finais"""
        fim = datetime.now()
        duracao = fim - self.stats['inicio']
        
        print("\n" + "="*50)
        print("📊 ESTATÍSTICAS FINAIS")
        print("="*50)
        print(f"📈 Total de vagas no arquivo: {self.stats['total_vagas']}")
        print(f"✅ Vagas inseridas com sucesso: {self.stats['vagas_inseridas']}")
        print(f"🏢 Empresas inseridas: {self.stats['empresas_inseridas']}")
        print(f"❌ Erros encontrados: {self.stats['erros']}")
        print(f"⏱️  Tempo total: {duracao}")
        print(f"📊 Taxa de sucesso: {(self.stats['vagas_inseridas']/self.stats['total_vagas']*100):.1f}%")
        
        if self.stats['vagas_inseridas'] > 0:
            print(f"\n🎉 Upload concluído com sucesso!")
            print(f"💡 Acesse o painel do Supabase para visualizar os dados")
        else:
            print(f"\n⚠️  Nenhuma vaga foi inserida. Verifique os dados e tente novamente.")

def main():
    print("🚀 UPLOAD DE VAGAS PARA SUPABASE")
    print("="*40)
    
    # Arquivo JSON com as vagas
    json_file = "vagas_todos_setores_estruturadas_completo.json"
    
    if not os.path.exists(json_file):
        print(f"❌ Arquivo {json_file} não encontrado")
        print("💡 Certifique-se de que o arquivo está no diretório atual")
        return
    
    try:
        uploader = SupabaseVagasUploader()
        uploader.load_and_upload_json(json_file)
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        print("\n🔧 Verifique:")
        print("   - Se as tabelas foram criadas no Supabase")
        print("   - Se as credenciais no .env estão corretas")
        print("   - Se a conexão com internet está funcionando")

if __name__ == "__main__":
    main()