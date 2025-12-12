from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Store, Product
from .forms import newstoreform, newproductform, newcontactform
from email.message import EmailMessage
import smtplib
from django.views.generic import ListView

def home(request):
    return render(request,'home.html')

def info(request):
    nombre=['¡DevOsvi']
    return render(request, 'info.html',{
        'name':nombre
    })

def stores_view(request):
    s = Store.objects.all()
    return render(request, 'stores.html', {
        'stores': s
    })

def products_view(request):
    p = Product.objects.all()
    return render(request,'products.html', {
        'products': p
    })

def create_store(request):
    if request.method=='GET':
        return render(request, 'create_store.html', {
            'forms': newstoreform()
        })
    else:
        Store.objects.create(
            name=request.POST['name'],
            description=request.POST['description']
        )
        return redirect('stores')

def create_product(request):
    if request.method == 'GET':
        return render(request, 'create_product.html', {
            'forms': newproductform(),
            'stores': Store.objects.all()
        })
    else:
        store_id = request.POST['store']
        store_obj = Store.objects.get(id=store_id)

        Product.objects.create(
            title=request.POST['title'],
            price=request.POST['price'],
            store=store_obj
        )

        return redirect('products')

def details(request, id):
    s = Store.objects.get(id=id)
    p = Product.objects.filter(store_id=id)
    return render(request,'details.html', {
        'store': s,
        'products': p
    })

def contact(request):
    if request.method == 'GET':
        return render(request, 'contact.html', {'form': newcontactform()})
    else:
        try:
            remitente = "programadores303@gmail.com"
            destinatario = request.POST['email']
            password_app = "vmtujjfepajxyrem"
             
            mensaje = """Saludos, gracias por contactarnos. Nuestros productos son los siguientes:\n\n"""
            
            for i in Product.objects.all():
                mensaje += f"{i} - ${i.price}\n"
            
            email = EmailMessage()
            email["From"] = remitente
            email["To"] = destinatario
            email["Subject"] = "Contacto tienda - Nuestros Productos DevLiz"
            email.set_content(mensaje)
            
            smtp = smtplib.SMTP("smtp.gmail.com", 587)
            smtp.starttls()
            smtp.login(remitente, password_app)
            smtp.sendmail(remitente, destinatario, email.as_string())
            smtp.quit()
            
            return redirect('home')
            
        except Exception as e:
            return render(request, 'contact.html', {
                'form': newcontactform(),
                'error': f'Error: {str(e)}'
            })

def despedirse(request):
    return HttpResponse('<h1>¡Adiós!</h1>')

class ProductosListView(ListView):
    context_object_name='productos'
    template_name = "filtro.html"

    def get_queryset(self):
        palabra_clave = self.request.GET.get("kword", "")
        return Product.objects.filter(title=palabra_clave)

def update_product(request):
    if request.method == "GET":

        if "kword" not in request.GET:
            return render(request, "update_product.html")

        nombre = request.GET.get("kword", "")

        try:
            product = Product.objects.get(title=nombre)
        except Product.DoesNotExist:
            return render(request, "update_product.html", {
                "error": "No existe un producto con ese nombre."
            })

        form = newproductform(initial={
            "title": product.title,
            "price": product.price,
            "store": product.store
        })

        return render(request, "update_product.html", {
            "forms": form,
            "product": product
        })

    else:
        nombre_original = request.POST.get("title_original")
        product = Product.objects.get(title=nombre_original)

        form = newproductform(request.POST)
        if form.is_valid():
            store_obj = Store.objects.get(id=form.cleaned_data["store"].id)

            product.title = form.cleaned_data["title"]
            product.price = form.cleaned_data["price"]
            product.store = store_obj
            product.save()

            return redirect("products")

        return render(request, "update_product.html", {
            "forms": form,
            "error": "Datos inválidos"
        })

def delete_product(request):
    context = {}

    if request.method == 'POST':
        kword = request.POST.get('kword', '').strip()

        if kword != "":
            try:
                obj = Product.objects.get(title__iexact=kword)
                obj.delete()
                context['mensaje'] = f"Producto '{kword}' eliminado correctamente."
            except Product.DoesNotExist:
                context['error'] = f"No se encontró el producto '{kword}'."

    return render(request, 'delete_product.html', context)

def update_store(request):
    if request.method == "GET":
        # El usuario todavía no ha buscado ninguna tienda
        if "kword" not in request.GET:
            return render(request, "update_store.html")

        # Buscar tienda por nombre
        nombre = request.GET.get("kword", "")
        try:
            store = Store.objects.get(name=nombre)
        except Store.DoesNotExist:
            return render(request, "update_store.html", {
                "error": "No existe una tienda con ese nombre."
            })

        # Mostrar el form con datos actuales
        form = newstoreform(initial={
            "name": store.name,
            "description": store.description
        })

        return render(request, "update_store.html", {
            "forms": form,
            "store": store
        })

    else:
        # Actualizar la tienda
        nombre_original = request.POST.get("name_original")
        store = Store.objects.get(name=nombre_original)

        form = newstoreform(request.POST)
        if form.is_valid():
            store.name = form.cleaned_data["name"]
            store.description = form.cleaned_data["description"]
            store.save()
            return redirect("stores")

        return render(request, "update_store.html", {
            "forms": form,
            "error": "Datos inválidos"
        })
    
def search_store(request):
    context = {}

    if request.method == "GET" and "kword" in request.GET:
        kword = request.GET.get("kword", "").strip()
        if kword != "":
            stores_found = Store.objects.filter(name__icontains=kword)
            context['stores'] = stores_found
            context['kword'] = kword

    return render(request, "search_store.html", context)

def delete_store(request):
    context = {}

    if request.method == "POST":
        kword = request.POST.get("kword", "").strip()
        if kword != "":
            try:
                store = Store.objects.get(name__iexact=kword)
                store.delete()
                context['mensaje'] = f"Tienda '{kword}' eliminada correctamente."
            except Store.DoesNotExist:
                context['error'] = f"No se encontró la tienda '{kword}'."

    return render(request, "delete_store.html", context)
