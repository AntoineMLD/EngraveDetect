from django.db import models


class Supplier(models.Model):
    """
    Modèle pour les fournisseurs de verres optiques.
    """
    supplier_name = models.CharField(max_length=255, unique=True, verbose_name="Nom du fournisseur")

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['supplier_name']

    def __str__(self):
        return self.supplier_name


class Material(models.Model):
    """
    Modèle pour les matériaux utilisés dans les verres optiques.
    """
    material_name = models.CharField(max_length=100, unique=True, verbose_name="Matériau")

    class Meta:
        verbose_name = "Matériau"
        verbose_name_plural = "Matériaux"
        ordering = ['material_name']

    def __str__(self):
        return self.material_name


class Glass(models.Model):
    """
    Modèle pour les verres optiques.
    """
    CATEGORY_CHOICES = [
        ('Single Vision', 'Vision simple'),
        ('Progressive', 'Progressif'),
        ('Bifocal', 'Bifocal'),
        ('Other', 'Autre'),
    ]

    glass_name = models.CharField(max_length=255, verbose_name="Nom du verre")
    glass_index = models.CharField(max_length=50, verbose_name="Indice du verre")
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, verbose_name="Matériau")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='glasses', verbose_name="Fournisseur")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other', verbose_name="Catégorie")
    nasal_engraving = models.CharField(max_length=100, blank=True, null=True, verbose_name="Gravure nasale")

    class Meta:
        verbose_name = "Verre optique"
        verbose_name_plural = "Verres optiques"
        unique_together = ('glass_name', 'glass_index', 'supplier', 'material')
        ordering = ['glass_name', 'glass_index']

    def __str__(self):
        return f"{self.glass_name} ({self.glass_index})"


class Engraving(models.Model):
    """
    Modèle pour les gravures sur les verres optiques.
    """
    glass = models.ForeignKey(Glass, on_delete=models.CASCADE, related_name='engravings', verbose_name="Verre optique")
    engraving_code = models.CharField(max_length=50, verbose_name="Code de gravure")
    description = models.TextField(blank=True, null=True, verbose_name="Description de la gravure")
    confidence = models.FloatField(default=0.0, verbose_name="Confiance de l'analyse")

    class Meta:
        verbose_name = "Gravure"
        verbose_name_plural = "Gravures"
        ordering = ['engraving_code']

    def __str__(self):
        return f"{self.engraving_code} (Confiance: {self.confidence:.2f})"


class ImageUpload(models.Model):
    """
    Modèle pour gérer les images uploadées par les utilisateurs pour l'analyse.
    """
    image = models.ImageField(upload_to='engraving_images/', verbose_name="Image de gravure")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    analyzed = models.BooleanField(default=False, verbose_name="Analysé")

    class Meta:
        verbose_name = "Image uploadée"
        verbose_name_plural = "Images uploadées"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Image {self.id} (Analysé: {'Oui' if self.analyzed else 'Non'})"
