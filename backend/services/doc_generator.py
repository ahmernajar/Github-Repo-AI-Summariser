import os
import json
import logging
from typing import Dict, List, Any
from openai import OpenAI
import markdown
from jinja2 import Template
from datetime import datetime

logger = logging.getLogger(__name__)

class DocGenerator:
    """Service for generating documentation using GPT-4"""
    
    def __init__(self):
        self.client = OpenAI(api_key="sk-proj-uaJQV2o....")
        self.output_dir = "sample_output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_documentation(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive documentation for a repository
        
        Args:
            repo_data: Repository data with extracted symbols
            
        Returns:
            Dictionary containing documentation URLs and metadata
        """
        try:
            logger.info(f"Generating documentation for {repo_data['repo_name']}")
            
            # Generate overview documentation
            overview_doc = await self._generate_overview(repo_data)
            
            # Generate module documentation
            module_docs = []
            for module in repo_data['modules']:
                module_doc = await self._generate_module_documentation(module)
                module_docs.append(module_doc)
            
            # Generate architecture diagram
            architecture_diagram = await self._generate_architecture_diagram(repo_data)
            
            # Create final documentation
            final_docs = {
                'overview': overview_doc,
                'modules': module_docs,
                'architecture': architecture_diagram,
                'metadata': {
                    'repo_name': repo_data['repo_name'],
                    'repo_url': repo_data['repo_url'],
                    'generated_at': datetime.now().isoformat(),
                    'total_modules': len(repo_data['modules']),
                    'total_files': repo_data['total_files']
                }
            }
            
            # Generate HTML documentation
            html_file = await self._create_html_documentation(final_docs)
            
            return {
                'doc_url': f'/docs/{html_file}',
                'documentation': final_docs,
                'file_path': html_file
            }
            
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            raise Exception(f"Documentation generation failed: {str(e)}")
    
    async def _generate_overview(self, repo_data: Dict[str, Any]) -> str:
        """Generate high-level overview of the repository"""
        try:
            # Create summary of all modules
            module_summary = []
            for module in repo_data['modules']:
                symbols = [s['name'] for s in module['symbols']]
                module_summary.append(f"- {module['module_name']}: {', '.join(symbols[:5])}")
            
            prompt = f"""
            Generate a comprehensive overview documentation for the Python repository '{repo_data['repo_name']}'.
            
            Repository contains {len(repo_data['modules'])} modules with the following structure:
            {chr(10).join(module_summary)}
            
            Please provide:
            1. A clear, engaging summary of what this repository does
            2. Main purpose and use cases
            3. Key components and their roles
            4. Getting started guide
            5. Installation instructions (if applicable)
            
            Write in a professional, user-friendly tone that would help both developers and non-technical users understand the project.
            Use markdown formatting for better readability.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating overview: {str(e)}")
            return f"# {repo_data['repo_name']}\n\nError generating overview: {str(e)}"
    
    async def _generate_module_documentation(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation for a specific module"""
        try:
            symbols_summary = []
            for symbol in module['symbols']:
                symbols_summary.append(f"- {symbol['type']}: {symbol['name']}")
            
            prompt = f"""
            Generate detailed documentation for the Python module '{module['module_name']}' located at '{module['file_path']}'.
            
            Module docstring: {module['docstring'] or 'No docstring available'}
            
            The module contains the following symbols:
            {chr(10).join(symbols_summary)}
            
            For each symbol, please provide:
            1. A clear explanation of what it does
            2. Parameters and return values (for functions/methods)
            3. Usage examples where appropriate
            4. Important notes or considerations
            
            Write in markdown format with proper headers and code blocks.
            Make it comprehensive but easy to understand.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            documentation = response.choices[0].message.content
            
            # Generate individual symbol documentation
            symbol_docs = []
            for symbol in module['symbols']:
                symbol_doc = await self._generate_symbol_documentation(symbol)
                symbol_docs.append(symbol_doc)
            
            return {
                'module_name': module['module_name'],
                'file_path': module['file_path'],
                'overview': documentation,
                'symbols': symbol_docs
            }
            
        except Exception as e:
            logger.error(f"Error generating module documentation: {str(e)}")
            return {
                'module_name': module['module_name'],
                'file_path': module['file_path'],
                'overview': f"Error generating documentation: {str(e)}",
                'symbols': []
            }
    
    async def _generate_symbol_documentation(self, symbol: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation for a specific symbol"""
        try:
            if symbol['type'] == 'class':
                methods_info = []
                for method in symbol.get('methods', []):
                    methods_info.append(f"- {method['name']}: {method['docstring'] or 'No docstring'}")
                
                prompt = f"""
                Generate detailed documentation for the Python class '{symbol['name']}'.
                
                Class docstring: {symbol['docstring'] or 'No docstring available'}
                Base classes: {', '.join(symbol.get('base_classes', []))}
                
                Methods:
                {chr(10).join(methods_info)}
                
                Please provide:
                1. What this class represents and its purpose
                2. Key functionality and use cases
                3. Simple usage example
                4. Important notes about initialization or usage
                
                Format as markdown with code examples.
                """
                
            elif symbol['type'] in ['function', 'method']:
                args_info = []
                for arg in symbol.get('args', []):
                    args_info.append(f"- {arg['name']}: {arg['annotation'] or 'Any'}")
                
                prompt = f"""
                Generate detailed documentation for the Python {symbol['type']} '{symbol['name']}'.
                
                Docstring: {symbol['docstring'] or 'No docstring available'}
                
                Parameters:
                {chr(10).join(args_info)}
                
                Returns: {symbol.get('returns', 'Not specified')}
                
                Please provide:
                1. What this {symbol['type']} does
                2. Parameter descriptions
                3. Return value description
                4. Usage example
                5. Any important notes or exceptions
                
                Format as markdown with code examples.
                """
                
            else:  # constant
                prompt = f"""
                Generate documentation for the Python constant '{symbol['name']}'.
                
                Value: {symbol.get('value', 'Not available')}
                
                Please provide:
                1. What this constant represents
                2. Its purpose and usage
                3. Simple usage example
                
                Format as markdown.
                """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            return {
                'name': symbol['name'],
                'type': symbol['type'],
                'documentation': response.choices[0].message.content,
                'metadata': symbol
            }
            
        except Exception as e:
            logger.error(f"Error generating symbol documentation: {str(e)}")
            return {
                'name': symbol['name'],
                'type': symbol['type'],
                'documentation': f"Error generating documentation: {str(e)}",
                'metadata': symbol
            }
    
    async def _generate_architecture_diagram(self, repo_data: Dict[str, Any]) -> str:
        """Generate a Mermaid architecture diagram"""
        try:
            # Create a simple, guaranteed-valid diagram based on repository structure
            modules_count = len(repo_data['modules'])
            total_symbols = sum(len(module['symbols']) for module in repo_data['modules'])
            
            # Get main modules (up to 3)
            main_modules = []
            for module in repo_data['modules'][:3]:
                if module['symbols']:  # Only include modules with symbols
                    module_name = module['module_name'].split('.')[-1]  # Get last part of module name
                    # Clean module name for Mermaid (remove special chars)
                    clean_name = ''.join(c for c in module_name if c.isalnum() or c in [' ', '-', '_'])
                    if clean_name:
                        main_modules.append(clean_name)
            
            # Create a clean repository name for Mermaid
            clean_repo_name = ''.join(c for c in repo_data['repo_name'] if c.isalnum() or c in [' ', '-', '_'])
            
            # Generate a simple, valid diagram
            diagram = f"""```mermaid
graph TD
    A[{clean_repo_name}] --> B[Core Modules]
    A --> C[Python Files]
    B --> D[Classes & Functions]
    C --> E[{modules_count} Modules]
    D --> F[{total_symbols} Symbols]"""
            
            # Add main modules if available
            if main_modules:
                for i, module in enumerate(main_modules):
                    letter = chr(ord('G') + i)  # G, H, I, etc.
                    diagram += f"\n    E --> {letter}[{module}]"
            
            diagram += "\n```"
            
            logger.info(f"Generated architecture diagram for {repo_data['repo_name']}")
            return diagram
            
        except Exception as e:
            logger.error(f"Error generating architecture diagram: {str(e)}")
            # Ultra-simple fallback
            return """```mermaid
graph TD
    A[Repository] --> B[Python Code]
    B --> C[Classes]
    B --> D[Functions]
    C --> E[Documentation Generated]
    D --> E
```"""
    
    async def _create_html_documentation(self, docs: Dict[str, Any]) -> str:
        """Create HTML documentation file"""
        try:
            html_template = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{{ metadata.repo_name }} - Documentation</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 0; text-align: center; margin-bottom: 30px; }
                    .header h1 { margin: 0; font-size: 2.5em; }
                    .header p { margin: 10px 0 0; opacity: 0.9; }
                    .content { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
                    .module { border-left: 4px solid #667eea; padding-left: 20px; margin-bottom: 30px; }
                    .symbol { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
                    .symbol-header { font-weight: bold; color: #333; margin-bottom: 10px; }
                    .toc { background: #e9ecef; padding: 20px; border-radius: 5px; margin-bottom: 30px; }
                    .toc ul { list-style-type: none; padding-left: 0; }
                    .toc li { margin: 5px 0; }
                    .toc a { text-decoration: none; color: #667eea; }
                    .toc a:hover { text-decoration: underline; }
                    pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
                    code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: 'Monaco', 'Menlo', monospace; }
                    .mermaid { text-align: center; margin: 20px 0; }
                    .metadata { color: #666; font-size: 0.9em; margin-top: 20px; }
                </style>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            </head>
            <body>
                <div class="header">
                    <h1>{{ metadata.repo_name }}</h1>
                    <p>Generated Documentation</p>
                    <p class="metadata">Generated on {{ metadata.generated_at.split('T')[0] }} | {{ metadata.total_modules }} modules | {{ metadata.total_files }} files</p>
                </div>
                
                <div class="container">
                    <div class="content">
                        <div class="toc">
                            <h2>Table of Contents</h2>
                            <ul>
                                <li><a href="#overview">Overview</a></li>
                                <li><a href="#architecture">Architecture</a></li>
                                <li><a href="#modules">Modules</a>
                                    <ul>
                                        {% for module in modules %}
                                        <li><a href="#{{ module.module_name }}">{{ module.module_name }}</a></li>
                                        {% endfor %}
                                    </ul>
                                </li>
                            </ul>
                        </div>
                        
                        <div id="overview">
                            <h2>Overview</h2>
                            {{ overview | safe }}
                        </div>
                        
                        <div id="architecture">
                            <h2>Architecture</h2>
                            <div class="mermaid">
                                {{ architecture | safe }}
                            </div>
                        </div>
                        
                        <div id="modules">
                            <h2>Modules</h2>
                            {% for module in modules %}
                            <div class="module" id="{{ module.module_name }}">
                                <h3>{{ module.module_name }}</h3>
                                <p><strong>File:</strong> {{ module.file_path }}</p>
                                {{ module.overview | safe }}
                                
                                {% if module.symbols %}
                                <h4>Symbols</h4>
                                {% for symbol in module.symbols %}
                                <div class="symbol">
                                    <div class="symbol-header">{{ symbol.type | title }}: {{ symbol.name }}</div>
                                    {{ symbol.documentation | safe }}
                                </div>
                                {% endfor %}
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <script>
                    mermaid.initialize({startOnLoad:true});
                </script>
            </body>
            </html>
            """
            
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=['codehilite', 'fenced_code'])
            docs['overview'] = md.convert(docs['overview'])
            
            # Clean architecture diagram for HTML (remove markdown code blocks)
            if docs['architecture'].startswith("```mermaid"):
                docs['architecture'] = docs['architecture'].replace("```mermaid\n", "").replace("```", "").strip()
            
            for module in docs['modules']:
                module['overview'] = md.convert(module['overview'])
                for symbol in module['symbols']:
                    symbol['documentation'] = md.convert(symbol['documentation'])
            
            template = Template(html_template)
            html_content = template.render(**docs)
            
            # Save to file
            filename = f"{docs['metadata']['repo_name']}_docs.html"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Documentation saved to {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating HTML documentation: {str(e)}")
            raise Exception(f"HTML generation failed: {str(e)}") 
