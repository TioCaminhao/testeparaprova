from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Noticia, Categoria
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

# Create your views here.
@login_required
def inicio_gerencia(request):
    return render(request, 'gerencia/inicio.html')

def listagem_noticia(request):
    formularioFiltro = NoticiaFilterForm(request.GET or None)
    
    noticias = Noticia.objects.filter(usuario=request.user)  # Filtra pelo usuário logado

    if formularioFiltro.is_valid():
        if formularioFiltro.cleaned_data['titulo']:
            noticias = noticias.filter(titulo__icontains=formularioFiltro.cleaned_data['titulo'])
        if formularioFiltro.cleaned_data['data_publicacao_inicio']:
            noticias = noticias.filter(data_publicacao__gte=formularioFiltro.cleaned_data['data_publicacao_inicio'])
        if formularioFiltro.cleaned_data['data_publicacao_fim']:
            noticias = noticias.filter(data_publicacao__lte=formularioFiltro.cleaned_data['data_publicacao_fim'])
        if formularioFiltro.cleaned_data['categoria']:
            noticias = noticias.filter(categoria=formularioFiltro.cleaned_data['categoria'])
    
    contexto = {
        'noticias': noticias,
        'formularioFiltro': formularioFiltro
    }
    return render(request, 'gerencia/listagem_noticia.html',contexto)


def cadastrar_noticia(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)  # Cria instância sem salvar
            noticia.usuario = request.user  # Atribui o autor (usuário logado)
            noticia.save()  # Salva a notícia no banco
            return redirect('gerencia:listagem_noticia')  # Redireciona para página de sucesso
    else:
        form = NoticiaForm() 

    contexto = {'form': form}
    return render(request, 'gerencia/cadastro_noticia.html', contexto)

@login_required
def editar_noticia(request, id):
    noticia = Noticia.objects.get(id=id)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            noticia_editada = form.save(commit=False)  # Não salva ainda
            noticia_editada.usuario = request.user 
            noticia_editada.save()  # Salva com o usuário intacto
            return redirect('gerencia:listagem_noticia')
    else:
        form = NoticiaForm(instance=noticia)
    
    contexto = {
        'form': form
    }
    return render(request, 'gerencia/cadastro_noticia.html',contexto)




def index(request):
    categoria_nome = request.GET.get('categoria')  # Obtém o parâmetro 'categoria' da URL
    search_query = request.GET.get('search')  # Obtém o parâmetro de busca

    # Filtra as notícias com base na categoria ou na busca
    noticias = Noticia.objects.all()
    if categoria_nome:
        categoria = Categoria.objects.filter(nome=categoria_nome).first()
        if categoria:
            noticias = noticias.filter(categoria=categoria)

    if search_query:
        noticias = noticias.filter(titulo__icontains=search_query)  # Filtra por título, ignorando maiúsculas/minúsculas

    categorias = Categoria.objects.all()  # Pega todas as categorias para exibir no template

    contexto = {
        'noticias': noticias,
        'categorias': categorias,
        'categoria_selecionada': categoria_nome,
        'search_query': search_query,
    }
    return render(request, 'gerencia/index.html', contexto)


def listagem_categoria(request):
    categorias = Categoria.objects.all()  # Obtemos o QuerySet inicial.
    
    # Aplicamos o filtro:
    formularioFiltro = CategoriaFilterForm(request.GET or None)
    if formularioFiltro.is_valid():
        if formularioFiltro.cleaned_data.get('nome'):
            categorias = categorias.filter(nome__icontains=formularioFiltro.cleaned_data['nome'])
    
    # Aplicamos a paginação:
    paginator = Paginator(categorias, 10)  # 10 itens por página
    page_number = request.GET.get('page')  # Obtém o número da página na URL
    page_obj = paginator.get_page(page_number)  # Retorna a página correspondente

    context = {
        'formularioFiltro': formularioFiltro,
        'categoria': page_obj,  # Enviamos a página para o template
    }
    return render(request, 'gerencia/listagem_categorias.html', context)

def cadastrar_categoria(request):
    if request.method == 'POST':
        form2 = CategoriaForm(request.POST, request.FILES)
        if form2.is_valid():
            categoria = form2.save(commit=False)  # Cria instância sem salvar
            categoria.usuario = request.user  # Atribui o autor (usuário logado)
            categoria.save()  # Salva a notícia no banco
            return redirect('gerencia:listagem_categorias')  # Redireciona para página de sucesso
    else:
        form2 = NoticiaForm() 

    contexto = {'form2': form2}
    return render(request, 'gerencia/cadastro_categoria.html', contexto)


@login_required
def editar_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    if request.method == 'POST':
        form2 = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form2.is_valid():
            noticia_editada = form2.save(commit=False)  # Não salva ainda
            noticia_editada.usuario = request.user 
            noticia_editada.save()  # Salva com o usuário intacto
            return redirect('gerencia:listagem_categorias')
    else:
        form2 = CategoriaForm(instance=categoria)
    
    contexto = {
        'form2': form2
    }
    return render(request, 'gerencia/cadastro_categoria.html',contexto)

def deletar_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.delete()
    return redirect('gerencia:listagem_categorias')