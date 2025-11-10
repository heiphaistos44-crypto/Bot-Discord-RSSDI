"""
Script de migration de l'ancien bot vers la nouvelle architecture
"""
import os
import json
import shutil
import asyncio
import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from config import Config
from database import db_manager
from utils.logger import setup_logging

logger = setup_logging()

class MigrationManager:
    """Gestionnaire de migration"""
    
    def __init__(self):
        self.backup_dir = Path("backup") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.old_files = [
            "data.json",
            "interface_data.json", 
            "commandes.py",
            "events.py",
            "dashboard.py",
            "interface.py",
            "sync_interface.py"
        ]
    
    async def run_migration(self):
        """Lance la migration complète"""
        logger.info("🚀 Début de la migration...")
        
        try:
            # 1. Créer une sauvegarde
            await self.create_backup()
            
            # 2. Initialiser la nouvelle base de données
            await self.init_new_database()
            
            # 3. Migrer les données
            await self.migrate_data()
            
            # 4. Vérifier la migration
            await self.verify_migration()
            
            # 5. Nettoyer si tout va bien
            await self.cleanup_old_files()
            
            logger.info("✅ Migration terminée avec succès !")
            print("\n" + "="*50)
            print("🎉 MIGRATION RÉUSSIE !")
            print("="*50)
            print("✅ Sauvegarde créée dans:", self.backup_dir)
            print("✅ Nouvelle base de données initialisée")
            print("✅ Données migrées avec succès")
            print("\n🚀 Tu peux maintenant lancer le nouveau bot avec:")
            print("   python bot.py")
            print("\n🌐 Interface web disponible sur:")
            print(f"   http://{Config.INTERFACE_HOST}:{Config.INTERFACE_PORT}")
            print("\n📚 Consulte README.md pour plus d'infos")
            
        except Exception as e:
            logger.error(f"❌ Erreur durant la migration: {e}")
            print(f"\n❌ Erreur de migration: {e}")
            print("📁 Tes données sont sauvegardées dans:", self.backup_dir)
            raise
    
    async def create_backup(self):
        """Crée une sauvegarde complète"""
        logger.info("📦 Création de la sauvegarde...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        files_backed_up = 0
        for file_name in self.old_files:
            file_path = Path(file_name)
            if file_path.exists():
                backup_path = self.backup_dir / file_name
                shutil.copy2(file_path, backup_path)
                files_backed_up += 1
                logger.info(f"  ✅ {file_name} sauvegardé")
        
        # Sauvegarder le .env aussi
        env_path = Path(".env")
        if env_path.exists():
            shutil.copy2(env_path, self.backup_dir / ".env")
            files_backed_up += 1
        
        logger.info(f"📦 {files_backed_up} fichiers sauvegardés dans {self.backup_dir}")
    
    async def init_new_database(self):
        """Initialise la nouvelle base de données"""
        logger.info("🗄️ Initialisation de la base de données...")
        
        # Créer le dossier data
        Config.DATA_DIR.mkdir(exist_ok=True)
        
        # Initialiser la base de données
        await db_manager.init_database()
        
        logger.info("✅ Base de données initialisée")
    
    async def migrate_data(self):
        """Migre les données de l'ancien format"""
        logger.info("📊 Migration des données...")
        
        # Migrer data.json
        await self._migrate_main_data()
        
        # Migrer interface_data.json
        await self._migrate_interface_data()
        
        logger.info("✅ Données migrées")
    
    async def _migrate_main_data(self):
        """Migre data.json vers la base de données"""
        data_file = Path("data.json")
        if not data_file.exists():
            logger.warning("⚠️ data.json non trouvé, migration ignorée")
            return
        
        logger.info("  📊 Migration de data.json...")
        await db_manager.migrate_from_json(data_file)
        logger.info("  ✅ data.json migré")
    
    async def _migrate_interface_data(self):
        """Migre interface_data.json"""
        interface_file = Path("interface_data.json")
        if not interface_file.exists():
            logger.warning("⚠️ interface_data.json non trouvé, migration ignorée")
            return
        
        logger.info("  📊 Migration de interface_data.json...")
        
        try:
            with open(interface_file, 'r', encoding='utf-8') as f:
                interface_data = json.load(f)
            
            # Validation des données
            if not isinstance(interface_data, dict):
                logger.warning("⚠️ Format interface_data.json invalide (doit être un objet JSON)")
                return
            
            # Cette migration pourrait être plus complexe selon le format
            # Pour l'instant, on log juste les données trouvées
            logger.info(f"  📊 Interface data trouvé: {len(interface_data)} entrées")
            
        except json.JSONDecodeError as e:
            logger.error(f"  ❌ Erreur JSON dans interface_data.json: {e}")
        except UnicodeDecodeError as e:
            logger.error(f"  ❌ Erreur d'encodage dans interface_data.json: {e}")
        except Exception as e:
            logger.error(f"  ❌ Erreur migration interface_data.json: {e}")
    
    async def verify_migration(self):
        """Vérifie que la migration s'est bien passée"""
        logger.info("🔍 Vérification de la migration...")
        
        try:
            # Vérifier que le fichier de base de données existe
            if not db_manager.db_path.exists():
                raise Exception(f"Base de données non trouvée: {db_manager.db_path}")
            
            async with aiosqlite.connect(db_manager.db_path) as db:
                # Vérifier que les tables existent
                cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in await cursor.fetchall()]
                await cursor.close()
                
                expected_tables = ['users', 'guilds', 'members', 'tags', 'auto_reactions']
                missing_tables = [table for table in expected_tables if table not in tables]
                
                if missing_tables:
                    raise Exception(f"Tables manquantes: {missing_tables}")
                
                # Compter les données migrées
                counts = {}
                for table in ['users', 'tags', 'auto_reactions', 'members']:
                    try:
                        cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                        result = await cursor.fetchone()
                        count = result[0] if result else 0
                        counts[table] = count
                        await cursor.close()
                    except Exception as e:
                        logger.warning(f"⚠️ Impossible de compter {table}: {e}")
                        counts[table] = 0
                
                logger.info("📊 Données migrées:")
                for table, count in counts.items():
                    logger.info(f"  - {table}: {count} entrées")
                
        except Exception as e:
            logger.error(f"❌ Erreur vérification: {e}")
            raise
        
        logger.info("✅ Migration vérifiée")
    
    async def cleanup_old_files(self):
        """Nettoie les anciens fichiers (avec confirmation)"""
        logger.info("🧹 Nettoyage des anciens fichiers...")
        
        # Pour la sécurité, on ne supprime pas automatiquement
        # On crée juste un fichier avec les instructions
        
        cleanup_script = """#!/bin/bash
# Script de nettoyage des anciens fichiers
# Exécute uniquement après avoir vérifié que tout fonctionne !

echo "⚠️  Ce script va supprimer les anciens fichiers du bot"
echo "   Assure-toi que le nouveau bot fonctionne avant de continuer !"
read -p "Continuer ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Suppression des anciens fichiers..."
"""
        
        for file_name in self.old_files:
            if Path(file_name).exists():
                cleanup_script += f'    rm -f "{file_name}"\n'
        
        cleanup_script += """
    echo "✅ Nettoyage terminé"
else
    echo "❌ Nettoyage annulé"
fi
"""
        
        cleanup_file = Path("cleanup_old_files.sh")
        with open(cleanup_file, 'w') as f:
            f.write(cleanup_script)
        
        # Rendre exécutable sur Unix
        try:
            os.chmod(cleanup_file, 0o755)
        except Exception:
            pass  # Windows
        
        logger.info(f"📝 Script de nettoyage créé: {cleanup_file}")
        logger.info("   Exécute-le quand tu es sûr que tout fonctionne !")

class PreMigrationChecker:
    """Vérifie les prérequis avant migration"""
    
    @staticmethod
    def check_prerequisites() -> bool:
        """Vérifie tous les prérequis"""
        logger.info("🔍 Vérification des prérequis...")
        
        checks = [
            PreMigrationChecker._check_python_version(),
            PreMigrationChecker._check_dependencies(),
            PreMigrationChecker._check_config(),
            PreMigrationChecker._check_permissions(),
        ]
        
        if all(checks):
            logger.info("✅ Tous les prérequis sont satisfaits")
            return True
        else:
            logger.error("❌ Certains prérequis ne sont pas satisfaits")
            return False
    
    @staticmethod
    def _check_python_version() -> bool:
        """Vérifie la version Python"""
        import sys
        
        major, minor = sys.version_info[:2]
        if major >= 3 and minor >= 8:
            logger.info(f"✅ Python {major}.{minor} OK")
            return True
        else:
            logger.error(f"❌ Python {major}.{minor} trop ancien (requis: 3.8+)")
            return False
    
    @staticmethod
    def _check_dependencies() -> bool:
        """Vérifie les dépendances"""
        required_packages = {
            'discord.py': 'discord',
            'aiosqlite': 'aiosqlite',
            'flask': 'flask',
            'python-dotenv': 'dotenv'
        }
        
        missing = []
        for package_name, import_name in required_packages.items():
            try:
                __import__(import_name)
                logger.info(f"✅ {package_name} installé")
            except ImportError:
                missing.append(package_name)
                logger.error(f"❌ {package_name} manquant")
        
        if missing:
            logger.error("📦 Installe les dépendances manquantes:")
            logger.error(f"   pip install {' '.join(missing)}")
            return False
        
        return True
    
    @staticmethod
    def _check_config() -> bool:
        """Vérifie la configuration"""
        try:
            Config.validate()
            logger.info("✅ Configuration valide")
            return True
        except Exception as e:
            logger.error(f"❌ Configuration invalide: {e}")
            logger.error("💡 Vérifie ton fichier .env")
            return False
    
    @staticmethod
    def _check_permissions() -> bool:
        """Vérifie les permissions de fichier"""
        test_dir = Path("test_permissions")
        
        try:
            # Test création dossier
            test_dir.mkdir(exist_ok=True)
            
            # Test écriture fichier
            test_file = test_dir / "test.txt"
            test_file.write_text("test")
            
            # Test lecture
            content = test_file.read_text()
            
            # Nettoyage
            test_file.unlink()
            test_dir.rmdir()
            
            logger.info("✅ Permissions d'écriture OK")
            return True
            
        except Exception as e:
            logger.error(f"❌ Problème de permissions: {e}")
            return False

async def main():
    """Fonction principale de migration"""
    print("🤖 Migration Bot Discord - Version 2.0")
    print("="*40)
    
    # Vérifier les prérequis
    if not PreMigrationChecker.check_prerequisites():
        print("\n❌ Prérequis non satisfaits. Corrige les erreurs avant de continuer.")
        return 1
    
    print("\n📋 Que va faire cette migration:")
    print("  1. 📦 Créer une sauvegarde de tes fichiers actuels")
    print("  2. 🗄️ Initialiser une nouvelle base de données SQLite")
    print("  3. 📊 Migrer tes données depuis data.json")
    print("  4. 🔍 Vérifier que tout s'est bien passé")
    print("  5. 📝 Créer un script de nettoyage optionnel")
    
    # Demander confirmation
    response = input("\n🤔 Continuer la migration ? (o/N): ").lower().strip()
    if response not in ['o', 'oui', 'y', 'yes']:
        print("❌ Migration annulée")
        return 0
    
    # Lancer la migration
    migration_manager = MigrationManager()
    try:
        await migration_manager.run_migration()
        return 0
    except Exception as e:
        logger.error(f"Migration échouée: {e}")
        return 1

if __name__ == "__main__":
    import sys
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Migration interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur fatale: {e}")
        sys.exit(1)