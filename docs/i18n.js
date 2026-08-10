// The page's copy, in the four languages it speaks.
//
// A plain global rather than four JSON files behind `fetch`: the strings have
// to be there before the first paint, and a fetch is a round-trip that happens
// after it. Loaded from <head>, this object is already in memory when the
// script at the end of the body goes to apply it.
//
// English is not just a row in here: it is written into the HTML as real
// content, so a reader with no JavaScript, and a crawler, get a whole page.
// The rows below overwrite it. Keys hold markup where the sentence has some
// (a link, a `<code>`), and it is applied as HTML, which is safe because this
// file is the only thing that writes it.
//
// What is deliberately NOT in here: the code samples. Their comments are code,
// and code is written in English on this project. A reader judging a theme by
// its Rust sample is looking at the colours, not reading the comment.
window.VIOLEETER_I18N = {
  en: {
    "meta.title": "Violeeter: a violet theme for everything",
    "meta.description": "A violet theme in dark and light, for your editor and your terminal. Every colour verified against WCAG AA, not guessed.",
    "og.description": "Dark and light. Every colour verified against WCAG AA, not guessed.",

    "lang.label": "Language",
    "brand.home": "Violeeter, home",
    "nav.install": "Install",
    "theme.to_light": "Switch to light",
    "theme.to_dark": "Switch to dark",

    "hero.h1": "A violet theme for everything.",
    "hero.lede": "Dark and light, for your editor and your terminal. Every colour that can carry text is verified against WCAG AA: measured, not guessed, and the build fails if one drops below.",
    "badge.variants": "Dark + Light",
    "badge.ports": "11 ports",
    "badge.aa": "AA verified",
    "badge.worn": "Worn by",

    "palette.h2": "The palette",
    "palette.lede": "Sixteen ANSI slots plus foreground, background and cursor. The dark variant sits on <code>#24203F</code>; the light one is not that flipped, it is each colour re-picked at a luminance that reads on a pale ground.",

    "contrast.h2": "Contrast, measured",
    "contrast.lede": "Most themes assert readability. This one measures it: every colour that can carry text is checked against its own background, and <code>python3 build.py --check</code> fails the build if one drops under 4.5:1.",
    "contrast.th_variant": "Variant",
    "contrast.th_background": "Background",
    "contrast.th_worst": "Worst text contrast",
    "contrast.th_wcag": "WCAG AA",
    "contrast.pass": "pass",
    "contrast.note": "Nothing is exempt, and two colours were changed to keep it that way. <code>white</code> and <code>brightWhite</code> in the light variant used to be, on the reasoning that they mean \"the palest thing here\" and so are surfaces. That is right about the name and wrong about the use: colour 7 is the default foreground of a large share of terminal programs. Under btop they measured 1.61:1 and the memory labels were not dim, they were absent.",

    "install.h2": "Install",
    "install.lede": "Every file is generated from one source, so the green in your editor is the green in your terminal.",
    "install.vscode_name": "VS Code: install it from the Marketplace",
    "install.vscode_note": "Both variants, no file to copy. Search for \u201cVioleeter\u201d in the Extensions view, or open the listing.",
    "install.vscode_cta": "Open the listing",
    "install.whole_h3": "Or take the whole set",
    "install.whole_lede": "Copying from above needs nothing installed. This is for when you want all of them at once.",

    "came.h2": "Where it came from",
    "came.lede_pre": "Violeeter was not designed on a colour wheel. It is the palette",
    "came.lede_post": " wears, a macOS terminal for running several coding agents at once, and it was tuned over months of being stared at for eight hours a day. That is the only reason its greys are legible and its blue is where it is: both were wrong first, in use.",
    "came.s1.name": "refactor the transcript reader",
    "came.s1.status": "waiting for you",
    "came.s2.name": "files panel",
    "came.s2.status": "working",
    "came.both": "Both pages you can reach from here are painted with this theme, and the terminal above ships with it built in. If a colour were wrong, it would be wrong in the thing its author uses all day, which is the only test of a theme that cannot be faked.",

    "porting.h2": "Porting it somewhere else",
    "porting.lede": "A port is a function in <code>build.py</code> that takes the palette and returns a string. Nothing is written by hand, and no port re-picks a colour. Editor ports also get <code>syntax</code>, the mapping from semantic role to palette slot, which is why a string is the same green everywhere.",
    "porting.after": "Add it to <code>EXPORTS</code>, run <code>python3 build.py</code>, open a pull request.",

    "glabs.eyebrow": "the wider constellation",
    "glabs.h2": "Held by <span>[GLabs]</span>.",
    "glabs.lede": "[GLabs] is the umbrella that ties the family together. This page is the visual language it speaks, and these are the two projects that wear it.",
    "glabs.flux_role": "the workflow · direct reference ↗",
    "glabs.violeet_role": "the product · direct reference ↗",

    "footer": "Violeeter is MIT licensed, by <a href=\"https://github.com/grippado\">grippado</a>. It is the palette <a href=\"https://grippado.github.io/violeet/\">Violeet</a> ships with. <a href=\"https://github.com/grippado/violeeter/blob/main/docs/BRAND_IDENTITY.md\">Brand identity</a>.",

    "viewer.dark": "Dark",
    "viewer.light": "Light",
    "viewer.copy": "Copy",
    "viewer.copied": "Copied",
    "viewer.raw": "Raw",
    "viewer.loading": "Loading…",
    "viewer.error": "Could not load {file}. Open it on GitHub instead.",
    "sw.copy_title": "Copy {value}",
    "sw.copy_aria": "Copy {slot} as {format}, {value}",
    "sw.copied": "Copied"
  },

  pt: {
    "meta.title": "Violeeter: um tema violeta para tudo",
    "meta.description": "Um tema violeta em claro e escuro, para o seu editor e o seu terminal. Toda cor verificada contra o WCAG AA, não chutada.",
    "og.description": "Claro e escuro. Toda cor verificada contra o WCAG AA, não chutada.",

    "lang.label": "Idioma",
    "brand.home": "Violeeter, início",
    "nav.install": "Instalar",
    "theme.to_light": "Mudar para o claro",
    "theme.to_dark": "Mudar para o escuro",

    "hero.h1": "Um tema violeta para tudo.",
    "hero.lede": "Claro e escuro, para o seu editor e o seu terminal. Toda cor capaz de carregar texto é verificada contra o WCAG AA: medida, não chutada, e o build falha se alguma ficar abaixo.",
    "badge.variants": "Claro + Escuro",
    "badge.ports": "11 ports",
    "badge.aa": "AA verificado",
    "badge.worn": "Vestido pelo",

    "palette.h2": "A paleta",
    "palette.lede": "Dezesseis slots ANSI mais frente, fundo e cursor. A variante escura assenta sobre <code>#24203F</code>; a clara não é essa invertida, é cada cor reescolhida numa luminância que se lê sobre fundo pálido.",

    "contrast.h2": "Contraste, medido",
    "contrast.lede": "A maioria dos temas afirma ser legível. Este mede: toda cor capaz de carregar texto é conferida contra o próprio fundo, e <code>python3 build.py --check</code> derruba o build se alguma cair abaixo de 4,5:1.",
    "contrast.th_variant": "Variante",
    "contrast.th_background": "Fundo",
    "contrast.th_worst": "Pior contraste de texto",
    "contrast.th_wcag": "WCAG AA",
    "contrast.pass": "passa",
    "contrast.note": "Nada fica de fora, e duas cores mudaram para continuar assim. <code>white</code> e <code>brightWhite</code> na variante clara ficavam de fora, sob o argumento de que significam \"a coisa mais pálida daqui\" e portanto são superfícies. Isso está certo sobre o nome e errado sobre o uso: a cor 7 é a frente padrão de boa parte dos programas de terminal. No btop elas mediram 1,61:1 e os rótulos de memória não estavam apagados, estavam ausentes.",

    "install.h2": "Instalação",
    "install.lede": "Todo arquivo é gerado de uma fonte só, então o verde do seu editor é o verde do seu terminal.",
    "install.vscode_name": "VS Code: instale pelo Marketplace",
    "install.vscode_note": "As duas variantes, sem arquivo para copiar. Busque por \u201cVioleeter\u201d na aba de extensões, ou abra a página.",
    "install.vscode_cta": "Abrir a página",
    "install.whole_h3": "Ou leve o conjunto inteiro",
    "install.whole_lede": "Copiar dali de cima não exige instalar nada. Isto aqui é para quando você quer todos de uma vez.",

    "came.h2": "De onde ele veio",
    "came.lede_pre": "Violeeter não foi desenhado numa roda de cores. É a paleta que o",
    "came.lede_post": " veste, um terminal macOS para rodar vários agentes de código ao mesmo tempo, e foi afinada ao longo de meses sendo encarada oito horas por dia. É o único motivo de seus cinzas serem legíveis e de seu azul estar onde está: os dois estavam errados primeiro, no uso.",
    "came.s1.name": "refatorar o leitor de transcript",
    "came.s1.status": "esperando você",
    "came.s2.name": "painel de arquivos",
    "came.s2.status": "trabalhando",
    "came.both": "As duas páginas que você alcança daqui são pintadas com este tema, e o terminal acima já vem com ele embutido. Se uma cor estivesse errada, estaria errada na coisa que o autor usa o dia inteiro, que é o único teste de tema impossível de forjar.",

    "porting.h2": "Portando para outro lugar",
    "porting.lede": "Um port é uma função no <code>build.py</code> que recebe a paleta e devolve uma string. Nada é escrito à mão, e nenhum port reescolhe uma cor. Ports de editor recebem também o <code>syntax</code>, o mapa de papel semântico para slot da paleta, e é por isso que uma string é o mesmo verde em todo lugar.",
    "porting.after": "Adicione ao <code>EXPORTS</code>, rode <code>python3 build.py</code>, abra um pull request.",

    "glabs.eyebrow": "a constelação maior",
    "glabs.h2": "Sob o guarda-chuva da <span>[GLabs]</span>.",
    "glabs.lede": "A [GLabs] é o guarda-chuva que conecta a família. Esta página é a linguagem visual que ela fala, e estes são os dois projetos que a vestem.",
    "glabs.flux_role": "o fluxo de trabalho · referência direta ↗",
    "glabs.violeet_role": "o produto · referência direta ↗",

    "footer": "Violeeter é licenciado sob MIT, por <a href=\"https://github.com/grippado\">grippado</a>. É a paleta que o <a href=\"https://grippado.github.io/violeet/\">Violeet</a> traz de fábrica. <a href=\"https://github.com/grippado/violeeter/blob/main/docs/BRAND_IDENTITY.md\">Identidade da marca</a>.",

    "viewer.dark": "Escuro",
    "viewer.light": "Claro",
    "viewer.copy": "Copiar",
    "viewer.copied": "Copiado",
    "viewer.raw": "Bruto",
    "viewer.loading": "Carregando…",
    "viewer.error": "Não deu para carregar {file}. Abra no GitHub.",
    "sw.copy_title": "Copiar {value}",
    "sw.copy_aria": "Copiar {slot} como {format}, {value}",
    "sw.copied": "Copiado"
  },

  es: {
    "meta.title": "Violeeter: un tema violeta para todo",
    "meta.description": "Un tema violeta en claro y oscuro, para tu editor y tu terminal. Cada color verificado contra WCAG AA, no adivinado.",
    "og.description": "Claro y oscuro. Cada color verificado contra WCAG AA, no adivinado.",

    "lang.label": "Idioma",
    "brand.home": "Violeeter, inicio",
    "nav.install": "Instalar",
    "theme.to_light": "Cambiar a claro",
    "theme.to_dark": "Cambiar a oscuro",

    "hero.h1": "Un tema violeta para todo.",
    "hero.lede": "Claro y oscuro, para tu editor y tu terminal. Todo color capaz de llevar texto se verifica contra WCAG AA: medido, no adivinado, y el build falla si alguno queda por debajo.",
    "badge.variants": "Claro + Oscuro",
    "badge.ports": "11 ports",
    "badge.aa": "AA verificado",
    "badge.worn": "Lo viste",

    "palette.h2": "La paleta",
    "palette.lede": "Dieciséis ranuras ANSI más frente, fondo y cursor. La variante oscura se asienta sobre <code>#24203F</code>; la clara no es esa invertida, es cada color reelegido a una luminancia que se lee sobre fondo pálido.",

    "contrast.h2": "Contraste, medido",
    "contrast.lede": "La mayoría de los temas afirma ser legible. Este lo mide: todo color capaz de llevar texto se contrasta contra su propio fondo, y <code>python3 build.py --check</code> tumba el build si alguno baja de 4,5:1.",
    "contrast.th_variant": "Variante",
    "contrast.th_background": "Fondo",
    "contrast.th_worst": "Peor contraste de texto",
    "contrast.th_wcag": "WCAG AA",
    "contrast.pass": "pasa",
    "contrast.note": "Nada queda exento, y dos colores cambiaron para que siguiera así. <code>white</code> y <code>brightWhite</code> en la variante clara lo estaban, con el argumento de que significan \"lo más pálido de aquí\" y por tanto son superficies. Eso acierta con el nombre y falla con el uso: el color 7 es el frente por defecto de buena parte de los programas de terminal. Bajo btop midieron 1,61:1 y las etiquetas de memoria no estaban tenues, estaban ausentes.",

    "install.h2": "Instalación",
    "install.lede": "Cada archivo se genera de una sola fuente, así que el verde de tu editor es el verde de tu terminal.",
    "install.vscode_name": "VS Code: instálalo desde el Marketplace",
    "install.vscode_note": "Las dos variantes, sin archivo que copiar. Busca \u201cVioleeter\u201d en la vista de extensiones, o abre la página.",
    "install.vscode_cta": "Abrir la página",
    "install.whole_h3": "O llévate el conjunto entero",
    "install.whole_lede": "Copiar de arriba no exige instalar nada. Esto es para cuando los quieres todos de una vez.",

    "came.h2": "De dónde salió",
    "came.lede_pre": "Violeeter no se diseñó en una rueda de color. Es la paleta que lleva puesta",
    "came.lede_post": ", una terminal de macOS para ejecutar varios agentes de código a la vez, y se afinó a lo largo de meses de mirarla ocho horas al día. Es la única razón de que sus grises sean legibles y de que su azul esté donde está: los dos estuvieron mal primero, en uso.",
    "came.s1.name": "refactorizar el lector de transcript",
    "came.s1.status": "te está esperando",
    "came.s2.name": "panel de archivos",
    "came.s2.status": "trabajando",
    "came.both": "Las dos páginas a las que llegas desde aquí están pintadas con este tema, y la terminal de arriba ya lo trae dentro. Si un color estuviera mal, estaría mal en la cosa que su autor usa todo el día, que es la única prueba de un tema imposible de falsear.",

    "porting.h2": "Portarlo a otro sitio",
    "porting.lede": "Un port es una función en <code>build.py</code> que recibe la paleta y devuelve un string. Nada se escribe a mano, y ningún port reelige un color. Los ports de editor reciben además <code>syntax</code>, el mapa de rol semántico a ranura de la paleta, y por eso un string es el mismo verde en todas partes.",
    "porting.after": "Añádelo a <code>EXPORTS</code>, ejecuta <code>python3 build.py</code>, abre un pull request.",

    "glabs.eyebrow": "la constelación mayor",
    "glabs.h2": "Bajo el paraguas de <span>[GLabs]</span>.",
    "glabs.lede": "[GLabs] es el paraguas que conecta a la familia. Esta página es el lenguaje visual que habla, y estos son los dos proyectos que lo visten.",
    "glabs.flux_role": "el flujo de trabajo · referencia directa ↗",
    "glabs.violeet_role": "el producto · referencia directa ↗",

    "footer": "Violeeter tiene licencia MIT, por <a href=\"https://github.com/grippado\">grippado</a>. Es la paleta con la que viene <a href=\"https://grippado.github.io/violeet/\">Violeet</a>. <a href=\"https://github.com/grippado/violeeter/blob/main/docs/BRAND_IDENTITY.md\">Identidad de marca</a>.",

    "viewer.dark": "Oscuro",
    "viewer.light": "Claro",
    "viewer.copy": "Copiar",
    "viewer.copied": "Copiado",
    "viewer.raw": "Crudo",
    "viewer.loading": "Cargando…",
    "viewer.error": "No se pudo cargar {file}. Ábrelo en GitHub.",
    "sw.copy_title": "Copiar {value}",
    "sw.copy_aria": "Copiar {slot} como {format}, {value}",
    "sw.copied": "Copiado"
  },

  de: {
    "meta.title": "Violeeter: ein violettes Theme für alles",
    "meta.description": "Ein violettes Theme in Dunkel und Hell, für deinen Editor und dein Terminal. Jede Farbe gegen WCAG AA geprüft, nicht geraten.",
    "og.description": "Dunkel und hell. Jede Farbe gegen WCAG AA geprüft, nicht geraten.",

    "lang.label": "Sprache",
    "brand.home": "Violeeter, Startseite",
    "nav.install": "Installieren",
    "theme.to_light": "Zu Hell wechseln",
    "theme.to_dark": "Zu Dunkel wechseln",

    "hero.h1": "Ein violettes Theme für alles.",
    "hero.lede": "Dunkel und hell, für deinen Editor und dein Terminal. Jede Farbe, die Text tragen kann, ist gegen WCAG AA geprüft: gemessen, nicht geraten, und der Build schlägt fehl, sobald eine darunter fällt.",
    "badge.variants": "Dunkel + Hell",
    "badge.ports": "11 Ports",
    "badge.aa": "AA geprüft",
    "badge.worn": "Getragen von",

    "palette.h2": "Die Palette",
    "palette.lede": "Sechzehn ANSI-Plätze plus Vordergrund, Hintergrund und Cursor. Die dunkle Variante sitzt auf <code>#24203F</code>; die helle ist nicht deren Umkehrung, sondern jede Farbe neu gewählt in einer Helligkeit, die sich auf blassem Grund liest.",

    "contrast.h2": "Kontrast, gemessen",
    "contrast.lede": "Die meisten Themes behaupten Lesbarkeit. Dieses misst sie: jede Farbe, die Text tragen kann, wird gegen ihren eigenen Hintergrund geprüft, und <code>python3 build.py --check</code> lässt den Build scheitern, sobald eine unter 4,5:1 fällt.",
    "contrast.th_variant": "Variante",
    "contrast.th_background": "Hintergrund",
    "contrast.th_worst": "Schlechtester Textkontrast",
    "contrast.th_wcag": "WCAG AA",
    "contrast.pass": "bestanden",
    "contrast.note": "Nichts ist ausgenommen, und zwei Farben wurden geändert, damit das so bleibt. <code>white</code> und <code>brightWhite</code> in der hellen Variante waren es, mit der Begründung, sie bedeuteten \"das Blasseste hier\" und seien damit Flächen. Das trifft den Namen und verfehlt den Gebrauch: Farbe 7 ist der Standard-Vordergrund eines großen Teils der Terminal-Programme. Unter btop maßen sie 1,61:1, und die Speicher-Labels waren nicht blass, sie waren weg.",

    "install.h2": "Installation",
    "install.lede": "Jede Datei wird aus einer einzigen Quelle erzeugt, also ist das Grün in deinem Editor das Grün in deinem Terminal.",
    "install.vscode_name": "VS Code: aus dem Marketplace installieren",
    "install.vscode_note": "Beide Varianten, keine Datei zum Kopieren. Suche in der Erweiterungsansicht nach \u201cVioleeter\u201d, oder öffne die Seite.",
    "install.vscode_cta": "Seite öffnen",
    "install.whole_h3": "Oder nimm den ganzen Satz",
    "install.whole_lede": "Für das Kopieren von oben muss nichts installiert sein. Das hier ist für den Fall, dass du alle auf einmal willst.",

    "came.h2": "Woher es kommt",
    "came.lede_pre": "Violeeter wurde nicht am Farbkreis entworfen. Es ist die Palette, die",
    "came.lede_post": " trägt, ein macOS-Terminal für mehrere Coding-Agents gleichzeitig, und sie wurde über Monate justiert, in denen jemand acht Stunden am Tag darauf geschaut hat. Nur deshalb sind ihre Grautöne lesbar und ihr Blau da, wo es ist: beides war zuerst falsch, im Gebrauch.",
    "came.s1.name": "Transcript-Reader refactoren",
    "came.s1.status": "wartet auf dich",
    "came.s2.name": "Dateien-Panel",
    "came.s2.status": "arbeitet",
    "came.both": "Beide Seiten, die du von hier erreichst, sind mit diesem Theme gemalt, und das Terminal oben bringt es eingebaut mit. Wäre eine Farbe falsch, wäre sie in dem Ding falsch, das ihr Autor den ganzen Tag benutzt, und das ist die einzige Theme-Prüfung, die sich nicht fälschen lässt.",

    "porting.h2": "Es woandershin portieren",
    "porting.lede": "Ein Port ist eine Funktion in <code>build.py</code>, die die Palette nimmt und einen String zurückgibt. Nichts wird von Hand geschrieben, und kein Port wählt eine Farbe neu. Editor-Ports bekommen zusätzlich <code>syntax</code>, die Zuordnung von semantischer Rolle zu Palettenplatz, und darum ist ein String überall dasselbe Grün.",
    "porting.after": "Trag ihn in <code>EXPORTS</code> ein, führe <code>python3 build.py</code> aus, öffne einen Pull Request.",

    "glabs.eyebrow": "die weitere Konstellation",
    "glabs.h2": "Unter dem Dach von <span>[GLabs]</span>.",
    "glabs.lede": "[GLabs] ist das Dach, das die Familie zusammenhält. Diese Seite ist die visuelle Sprache, die es spricht, und das sind die beiden Projekte, die sie tragen.",
    "glabs.flux_role": "der Workflow · direkter Verweis ↗",
    "glabs.violeet_role": "das Produkt · direkter Verweis ↗",

    "footer": "Violeeter steht unter MIT-Lizenz, von <a href=\"https://github.com/grippado\">grippado</a>. Es ist die Palette, die <a href=\"https://grippado.github.io/violeet/\">Violeet</a> mitbringt. <a href=\"https://github.com/grippado/violeeter/blob/main/docs/BRAND_IDENTITY.md\">Markenidentität</a>.",

    "viewer.dark": "Dunkel",
    "viewer.light": "Hell",
    "viewer.copy": "Kopieren",
    "viewer.copied": "Kopiert",
    "viewer.raw": "Roh",
    "viewer.loading": "Lädt…",
    "viewer.error": "{file} konnte nicht geladen werden. Öffne die Datei auf GitHub.",
    "sw.copy_title": "{value} kopieren",
    "sw.copy_aria": "{slot} als {format} kopieren, {value}",
    "sw.copied": "Kopiert"
  }
};
