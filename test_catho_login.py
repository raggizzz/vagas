#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o login no Catho e diagnosticar problemas
"""

import time
from scraper import CathoProvider

def test_catho_login():
    """Testa o login no Catho com diagnóstico detalhado"""
    print("=== Teste de Login no Catho ===")
    
    # Criar provider
    provider = CathoProvider()
    
    try:
        # Configurar driver
        print("\n1. Configurando driver...")
        if not provider._setup_driver():
            print("❌ Falha ao configurar driver")
            return False
        print("✅ Driver configurado com sucesso")
        
        # Navegar para página inicial
        print("\n2. Navegando para página inicial...")
        provider.driver.get("https://www.catho.com.br")
        time.sleep(2)
        print(f"✅ Página carregada: {provider.driver.title}")
        
        # Verificar se já está logado
        print("\n3. Verificando status de login inicial...")
        current_url = provider.driver.current_url
        print(f"URL atual: {current_url}")
        
        # Procurar indicadores de login
        logged_indicators = [
            '[data-testid="user-menu"]',
            '.user-menu',
            '.profile-menu',
            '.logout',
            '.minha-conta'
        ]
        
        already_logged = False
        for indicator in logged_indicators:
            elements = provider.driver.find_elements('css selector', indicator)
            if elements:
                print(f"✅ Indicador de login encontrado: {indicator}")
                already_logged = True
                break
        
        if not already_logged:
            print("ℹ️ Usuário não está logado")
            
            # Tentar login
            print("\n4. Tentando fazer login...")
            login_success = provider._login_if_needed()
            
            if login_success:
                print("✅ Login executado (verificando resultado...)")
                
                # Verificar novamente se está logado
                time.sleep(3)
                current_url = provider.driver.current_url
                print(f"URL após login: {current_url}")
                
                for indicator in logged_indicators:
                    elements = provider.driver.find_elements('css selector', indicator)
                    if elements:
                        print(f"✅ Login confirmado - indicador encontrado: {indicator}")
                        return True
                
                print("⚠️ Login pode ter falhado - nenhum indicador encontrado")
                
                # Verificar se ainda está na página de login
                if 'login' in current_url.lower():
                    print("❌ Ainda na página de login")
                    
                    # Capturar screenshot para debug
                    try:
                        provider.driver.save_screenshot("catho_login_debug.png")
                        print("📸 Screenshot salva: catho_login_debug.png")
                    except:
                        pass
                        
                    # Verificar se há mensagens de erro
                    error_selectors = [
                        '.error-message',
                        '.alert-danger',
                        '.login-error',
                        '[data-testid="error"]'
                    ]
                    
                    for selector in error_selectors:
                        error_elements = provider.driver.find_elements('css selector', selector)
                        for element in error_elements:
                            if element.text.strip():
                                print(f"❌ Erro encontrado: {element.text}")
                
                return False
            else:
                print("❌ Falha no processo de login")
                return False
        else:
            print("✅ Usuário já estava logado")
            return True
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False
        
    finally:
        # Fechar driver
        if provider.driver:
            try:
                provider.driver.quit()
                print("\n🔒 Driver fechado")
            except:
                pass

if __name__ == "__main__":
    success = test_catho_login()
    
    if success:
        print("\n🎉 SUCESSO! Login no Catho funcionando")
    else:
        print("\n😞 FALHA! Problema com login no Catho")
        print("\n💡 Possíveis causas:")
        print("   1. Credenciais incorretas")
        print("   2. Catho mudou a estrutura da página de login")
        print("   3. Captcha ou verificação adicional")
        print("   4. Bloqueio por detecção de bot")