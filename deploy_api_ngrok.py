#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para fazer deploy da API de vagas no ngrok
Permite acesso público à API que consulta o Supabase
"""

import subprocess
import time
import os
import sys
from pathlib import Path

def check_ngrok_installed():
    """Verifica se o ngrok está instalado"""
    ngrok_path = Path("ngrok.exe")
    if ngrok_path.exists():
        print("✅ ngrok encontrado no diretório atual")
        return str(ngrok_path)
    
    # Verifica se está no PATH
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok encontrado no PATH do sistema")
            return "ngrok"
    except FileNotFoundError:
        pass
    
    print("❌ ngrok não encontrado")
    print("💡 Baixe o ngrok em: https://ngrok.com/download")
    return None

def check_api_file():
    """Verifica se o arquivo da API existe"""
    api_files = [
        "api_supabase_vagas.py",
        "api_vagas.py"
    ]
    
    for api_file in api_files:
        if Path(api_file).exists():
            print(f"✅ Arquivo da API encontrado: {api_file}")
            return api_file
    
    print("❌ Nenhum arquivo de API encontrado")
    print("💡 Certifique-se de que api_supabase_vagas.py ou api_vagas.py existe")
    return None

def start_api_server(api_file, port=5000):
    """Inicia o servidor da API"""
    print(f"🚀 Iniciando servidor da API na porta {port}...")
    
    try:
        # Inicia o servidor Flask
        process = subprocess.Popen(
            [sys.executable, api_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguarda um pouco para o servidor iniciar
        time.sleep(3)
        
        if process.poll() is None:
            print(f"✅ Servidor da API iniciado com sucesso (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erro ao iniciar servidor: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def start_ngrok_tunnel(ngrok_path, port=5000):
    """Inicia o túnel ngrok"""
    print(f"🌐 Criando túnel ngrok para porta {port}...")
    
    try:
        # Inicia o ngrok
        process = subprocess.Popen(
            [ngrok_path, "http", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguarda um pouco para o túnel ser criado
        time.sleep(5)
        
        if process.poll() is None:
            print(f"✅ Túnel ngrok criado com sucesso (PID: {process.pid})")
            print("🌍 Acesse http://localhost:4040 para ver a URL pública")
            print("📱 Sua API está disponível publicamente!")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Erro ao criar túnel: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao criar túnel ngrok: {e}")
        return None

def main():
    """Função principal"""
    print("🚀 DEPLOY DA API NO NGROK")
    print("=" * 50)
    
    # Verifica dependências
    ngrok_path = check_ngrok_installed()
    if not ngrok_path:
        return
    
    api_file = check_api_file()
    if not api_file:
        return
    
    print("\n📋 INICIANDO DEPLOY...")
    print("=" * 30)
    
    # Inicia o servidor da API
    api_process = start_api_server(api_file)
    if not api_process:
        return
    
    # Inicia o túnel ngrok
    ngrok_process = start_ngrok_tunnel(ngrok_path)
    if not ngrok_process:
        api_process.terminate()
        return
    
    print("\n🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
    print("=" * 40)
    print("📍 Endpoints disponíveis:")
    print("   • GET /vagas - Lista todas as vagas")
    print("   • GET /vagas/<id> - Detalhes de uma vaga")
    print("   • GET /empresas - Lista todas as empresas")
    print("   • GET /health - Status da API")
    print("\n🌐 Acesse http://localhost:4040 para ver a URL pública")
    print("\n⚠️  Pressione Ctrl+C para parar os serviços")
    
    try:
        # Mantém os processos rodando
        while True:
            time.sleep(1)
            
            # Verifica se os processos ainda estão rodando
            if api_process.poll() is not None:
                print("❌ Servidor da API parou inesperadamente")
                break
                
            if ngrok_process.poll() is not None:
                print("❌ Túnel ngrok parou inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Parando serviços...")
        
    finally:
        # Limpa os processos
        if api_process and api_process.poll() is None:
            api_process.terminate()
            print("✅ Servidor da API parado")
            
        if ngrok_process and ngrok_process.poll() is None:
            ngrok_process.terminate()
            print("✅ Túnel ngrok parado")
        
        print("👋 Deploy finalizado!")

if __name__ == "__main__":
    main()