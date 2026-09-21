%% -------------------------- Identificaçao ----------------------------
%% Classe LaTeX gerada por el comite editorial de la revista Ingenius.
%% Revista "Ingenius"  Universidad Politécnica Salesiana Ecuador.
%% Contacto e-mail: jcalle@ups.edu.ec
\ProvidesClass{ingenius}%[2021/03/22 -- v1.0 Ingenius] 
\typeout{Ingenius -- Revista de Ciencia y Tecnología}
\typeout{Universidad Politécnica Salesiana del Ecuador}
\typeout{Mas información -- http://ingenius.ups.edu.ec/}
\NeedsTeXFormat{LaTeX2e}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\LoadClass{article}    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                  Carga de  Paquetes Requeridos                        
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\RequirePackage{multirow}
\RequirePackage[utf8]{inputenc}
\RequirePackage{multicol}
\RequirePackage{balance}
\RequirePackage{titlesec}
%\RequirePackage{pifont}
\RequirePackage{float}
\RequirePackage{microtype}
\DisableLigatures[f]{encoding=*,family=*}
\RequirePackage{blindtext}
\RequirePackage{textpos}
\RequirePackage{xcolor}
\RequirePackage{color}
\RequirePackage{amsmath}
\RequirePackage{booktabs}
\RequirePackage[T1]{fontenc}
\RequirePackage[spanish,english]{babel}
\RequirePackage[font={small},tablename=Tabla,labelfont={bf,small},labelsep=period]{caption}
\RequirePackage{graphicx}
\RequirePackage{setspace}
\RequirePackage{lmodern}
\RequirePackage[obeyspaces,spaces]{url}
    \urlstyle{same}
\RequirePackage[papersize={21cm,28cm},twoside,top=2.25cm,bottom=1.75cm,left=2.5cm,right=1.8cm,headheight=2cm,headsep=.65cm,footskip=0.85cm]{geometry}
\RequirePackage[colorlinks,linkcolor=black,urlcolor=black,citecolor=black,breaklinks=true,%
                bookmarks=true,pdfstartview=XYZ]{hyperref}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     Definicion de palabras clave                  %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\newcommand{\titulo}[1]%
  {\newcommand\@titulo{#1}}

\newcommand{\tituloa}[1]%
  {\newcommand\@tituloa{#1}}

\newcommand{\autores}[1]%
  {\newcommand\@autores{#1}}

\newcommand{\adscripcionautor}[1]%
  {\newcommand\@adscripcionautor{#1}}

\newcommand{\fechar}[1]%
  {\newcommand\@fechar{#1}}

\newcommand{\fechaa}[1]%
  {\newcommand\@fechaa{#1}}

\newcommand{\ano}[1]%
  {\newcommand\@ano{#1}}

\newcommand{\mes}[1]%
  {\newcommand\@mes{#1}}

\newcommand{\numero}[1]%
  {\newcommand\@numero{#1}}

\newcommand{\autorad}[1]%
  {\newcommand\@autorad{#1}}

\newcommand{\pag}[1]%
  {\newcommand\@pag{#1}}

\newcommand{\dist}[1]%
  {\newcommand\@dist{#1}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                            Definicion  de nuevos campos                                          %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\newcommand{\eq}[1]{Ecuaci\'on~(\ref{#1}),} %% Use el comando \eq{label} y se obtendrá Ecuación (1), texto texo
\newcommand{\figu}[1]{Figura~\ref{#1},}       %% Use el comando \figu{label} y se obtendrá Figura 1, texto texo                  
\newcommand{\tab}[1]{Tabla~\ref{#1},}         %% Use el comando \tab{label} y se obtendrá Tabla 1, texto texo   

\newcommand\membrete{%

  \thispagestyle{plain}
  \begin{center}

    \begin{minipage}{0.9\textwidth}
        \centering\Large
        \begin{spacing}{1.1}
%\vspace{0.5cm}
        {\huge\textsc{\@titulo}}\\[18pt]
 {\huge\textsc{\@tituloa}}\\[8pt]
            {\large \@autores}
        \end{spacing}
    \end{minipage}
  \end{center}
}

\newcommand\adscripcion{%
%\vspace{1.5cm}
\noindent \rule{475pt}{0.6pt}
\begin{spacing}{0.85}
\noindent
{\small{\@adscripcionautor}}\\[4pt]%\textit
%{\small{Recibido: \@fechar}}, {\small{aprobado tras revisi\'on: \@fechaa}}\\[3pt]
%{\small Forma sugerida de citaci\'on: \@autorad  \, (\@ano). {«\@titulo\!\!~»}. {\textsc{Ingenius}}. N.$^\circ$\@numero, (\@mes). pp. \@pag. ISSN: 1390-650X.} 
\end{spacing}
}

  \newenvironment{resumenespanol}{%
      \begin{flushleft}%
        \bfseries \normalsize Resumen
	\phantomsection
      \end{flushleft}
 %\quotation
}

  \newenvironment{resumeningles}{%
      \begin{flushleft}%
        \bfseries \normalsize Abstract
	\phantomsection
      \end{flushleft}

% \quotation
}

\newcommand{\keywords}[1]{\vspace{\baselineskip}\parindent 0pt\textit{\textbf{Keywords}}: #1}
\newcommand{\palabrasclave}[1]{\vspace{\baselineskip}\parindent 0pt\textbf{\textit{Palabras clave}}: #1}

\newcommand\blfootnote[1]{%
  \begingroup
  \renewcommand\thefootnote{}\footnote{#1}%
  \addtocounter{footnote}{-1}%
  \endgroup
}
