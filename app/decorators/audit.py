"""
Decorators para Auditoria Automática
Facilitam a integração de logs de auditoria nas rotas administrativas
"""
from functools import wraps
from flask import request
from flask_login import current_user
from app.services.audit_service import audit_service


def audit_action(action, resource_type, get_resource_info=None):
    """
    Decorator genérico para auditar ações administrativas
    
    Args:
        action: Tipo de ação (CREATE, UPDATE, DELETE, etc.)
        resource_type: Tipo de recurso (User, Challenge, etc.)
        get_resource_info: Função para extrair informações do recurso da resposta
    
    Usage:
        @audit_action('CREATE', 'User', lambda r: {'id': r.id, 'name': r.name})
        def create_user():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Executar a função original
            result = f(*args, **kwargs)
            
            # Se o usuário está autenticado e é admin
            if current_user.is_authenticated and current_user.is_admin:
                try:
                    # Extrair informações do recurso se fornecido
                    resource_id = None
                    description = f"{action} {resource_type}"
                    changes = None
                    
                    if get_resource_info and result:
                        info = get_resource_info(result)
                        resource_id = info.get('id')
                        description = info.get('description', description)
                        changes = info.get('changes')
                    
                    # Registrar log
                    audit_service.log_action(
                        admin_id=current_user.id,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        description=description,
                        changes=changes
                    )
                except Exception as e:
                    # Não falhar a requisição se o log falhar
                    print(f"Erro ao registrar log de auditoria: {e}")
            
            return result
        return decorated_function
    return decorator


def audit_create(resource_type):
    """
    Decorator específico para criação de recursos
    
    Usage:
        @audit_create('User')
        def create_user():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            if current_user.is_authenticated and current_user.is_admin:
                try:
                    # Tentar extrair ID e nome do resultado
                    resource_id = kwargs.get('id') or getattr(result, 'id', None)
                    resource_name = kwargs.get('name') or getattr(result, 'name', None) or str(resource_id)
                    
                    audit_service.log_create(
                        admin_id=current_user.id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name
                    )
                except Exception as e:
                    print(f"Erro ao registrar log de criação: {e}")
            
            return result
        return decorated_function
    return decorator


def audit_update(resource_type, get_old_data=None, get_new_data=None):
    """
    Decorator específico para atualização de recursos
    
    Args:
        resource_type: Tipo de recurso
        get_old_data: Função para obter dados antigos
        get_new_data: Função para obter dados novos
    
    Usage:
        @audit_update('User', lambda: user.to_dict(), lambda: form.data)
        def update_user(user_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Capturar dados antigos antes da atualização
            old_data = {}
            if get_old_data:
                try:
                    old_data = get_old_data()
                except:
                    pass
            
            # Executar atualização
            result = f(*args, **kwargs)
            
            if current_user.is_authenticated and current_user.is_admin:
                try:
                    # Capturar dados novos após atualização
                    new_data = {}
                    if get_new_data:
                        try:
                            new_data = get_new_data()
                        except:
                            pass
                    
                    resource_id = kwargs.get('id') or getattr(result, 'id', None)
                    resource_name = kwargs.get('name') or getattr(result, 'name', None) or str(resource_id)
                    
                    audit_service.log_update(
                        admin_id=current_user.id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        old_data=old_data,
                        new_data=new_data
                    )
                except Exception as e:
                    print(f"Erro ao registrar log de atualização: {e}")
            
            return result
        return decorated_function
    return decorator


def audit_delete(resource_type):
    """
    Decorator específico para exclusão de recursos
    
    Usage:
        @audit_delete('User')
        def delete_user(user_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Tentar capturar dados antes da exclusão
            resource_id = kwargs.get('id') or args[0] if args else None
            resource_name = str(resource_id)
            data = None
            
            # Executar exclusão
            result = f(*args, **kwargs)
            
            if current_user.is_authenticated and current_user.is_admin:
                try:
                    audit_service.log_delete(
                        admin_id=current_user.id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        data=data
                    )
                except Exception as e:
                    print(f"Erro ao registrar log de exclusão: {e}")
            
            return result
        return decorated_function
    return decorator


def audit_view(resource_type):
    """
    Decorator para auditar visualização de dados sensíveis
    
    Usage:
        @audit_view('User')
        def view_user_details(user_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            if current_user.is_authenticated and current_user.is_admin:
                try:
                    resource_id = kwargs.get('id') or args[0] if args else None
                    resource_name = str(resource_id)
                    
                    audit_service.log_view(
                        admin_id=current_user.id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name
                    )
                except Exception as e:
                    print(f"Erro ao registrar log de visualização: {e}")
            
            return result
        return decorated_function
    return decorator
