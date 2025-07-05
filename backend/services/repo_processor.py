import os
import ast
import tempfile
import shutil
from typing import Dict, List, Any
from git import Repo
import logging

logger = logging.getLogger(__name__)

class RepoProcessor:
    """Service for processing GitHub repositories and extracting Python symbols"""
    
    def __init__(self):
        self.temp_dir = None
        
    async def process_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Process a GitHub repository and extract all Python symbols
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary containing repository data and extracted symbols
        """
        try:
            # Clone repository
            repo_data = await self._clone_repository(repo_url)
            
            # Extract Python files
            python_files = self._find_python_files(repo_data['local_path'])
            
            # Parse each Python file
            parsed_modules = []
            for file_path in python_files:
                try:
                    module_data = self._parse_python_file(file_path, repo_data['local_path'])
                    if module_data['symbols']:  # Only include modules with symbols
                        parsed_modules.append(module_data)
                except Exception as e:
                    logger.warning(f"Error parsing {file_path}: {str(e)}")
                    continue
            
            # Clean up temporary directory
            self._cleanup()
            
            return {
                'repo_url': repo_url,
                'repo_name': repo_data['name'],
                'modules': parsed_modules,
                'total_files': len(python_files),
                'parsed_modules': len(parsed_modules)
            }
            
        except Exception as e:
            self._cleanup()
            raise Exception(f"Error processing repository: {str(e)}")
    
    async def _clone_repository(self, repo_url: str) -> Dict[str, str]:
        """Clone repository to temporary directory"""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            
            # Extract repository name from URL
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            
            # Clone repository (shallow clone for speed)
            logger.info(f"Cloning repository: {repo_url}")
            repo = Repo.clone_from(repo_url, self.temp_dir, depth=1)
            
            return {
                'name': repo_name,
                'local_path': self.temp_dir,
                'url': repo_url
            }
            
        except Exception as e:
            raise Exception(f"Error cloning repository: {str(e)}")
    
    def _find_python_files(self, repo_path: str) -> List[str]:
        """Find all Python files in the repository"""
        python_files = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _parse_python_file(self, file_path: str, repo_root: str) -> Dict[str, Any]:
        """Parse a Python file and extract symbols"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Get relative path from repo root
            rel_path = os.path.relpath(file_path, repo_root)
            
            # Extract module information
            module_info = {
                'file_path': rel_path,
                'module_name': self._get_module_name(rel_path),
                'docstring': ast.get_docstring(tree),
                'symbols': []
            }
            
            # Extract symbols
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if not node.name.startswith('_'):  # Public classes only
                        class_info = self._extract_class_info(node)
                        module_info['symbols'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Public functions only
                        func_info = self._extract_function_info(node)
                        module_info['symbols'].append(func_info)
                
                elif isinstance(node, ast.Assign):
                    # Extract constants (uppercase variables)
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            const_info = self._extract_constant_info(node, target.id)
                            module_info['symbols'].append(const_info)
            
            return module_info
            
        except Exception as e:
            raise Exception(f"Error parsing {file_path}: {str(e)}")
    
    def _get_module_name(self, rel_path: str) -> str:
        """Convert file path to module name"""
        return rel_path.replace('/', '.').replace('.py', '')
    
    def _extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract information from a class definition"""
        methods = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                method_info = self._extract_function_info(item, is_method=True)
                methods.append(method_info)
        
        return {
            'type': 'class',
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'methods': methods,
            'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)],
            'line_number': node.lineno
        }
    
    def _extract_function_info(self, node: ast.FunctionDef, is_method: bool = False) -> Dict[str, Any]:
        """Extract information from a function definition"""
        args = []
        
        for arg in node.args.args:
            args.append({
                'name': arg.arg,
                'annotation': ast.unparse(arg.annotation) if arg.annotation else None
            })
        
        return {
            'type': 'method' if is_method else 'function',
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': args,
            'returns': ast.unparse(node.returns) if node.returns else None,
            'line_number': node.lineno
        }
    
    def _extract_constant_info(self, node: ast.Assign, name: str) -> Dict[str, Any]:
        """Extract information from a constant assignment"""
        try:
            value = ast.unparse(node.value)
        except:
            value = "Complex expression"
        
        return {
            'type': 'constant',
            'name': name,
            'value': value,
            'line_number': node.lineno
        }
    
    def _cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None 