# Clonar de la branch dev
git clone https://github.com/TFG-NeoBioRecon/NeoBioRecon.git -b dev

# Pasos para subir los cambios:
git add .
git commit -m "Comentario del commit"
git push

# Pasos para sincronizar lo de la nube con el PC:
git pull
**NUNCA hacer cambios en local sin hacer previamente el git pull** 

# Cambair de branch
git switch dev
git switch main

# Crear Branch a partir de otra Branch
git branch -c new old

# Publicar nueva Branch
git push -u origin dev