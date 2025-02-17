# Pour une nouvelle fonctionnalité
git checkout dev
git checkout -b feature/ma-fonctionnalite

# ... développement ...
git add .
git commit -m "feat: ma nouvelle fonctionnalité"
git push -u origin feature/ma-fonctionnalite

# Créer une PR vers dev sur GitHub
# Une fois la PR mergée dans dev :
git checkout dev
git pull origin dev

# Créer une PR de dev vers main sur GitHub