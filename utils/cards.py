
# ------------------------------------------------------------
# Gerador de Cards para Google Chat
# ------------------------------------------------------------
def card_contato_suporte():
    return {
                "cardsV2": [
            {
                "cardId": "contato_suporte",
                "card": {
                    "header": {
                        "title": "Canais de Contato",
                        "subtitle": "Entre em contato conosco pelo chat ou escolha uma das opções de contato abaixo:",
                        "imageUrl": "https://www.irib.org.br/app/webroot/files/downloads/images/ONR%20logo.PNG",
                        "imageType": "SQUARE",
                        "imageAltText": "Suporte"
                    },
                    "sections": [
                        {
                            "header": "Canais de Atendimento",
                            "widgets": [
                                {
                                    "decoratedText": {
                                        "startIcon": {"knownIcon": "EMAIL"},
                                        "text": "<b>E-mail:</b> <a href=\"mailto:oficioeletronico@onr.org.br\">oficioeletronico@onr.org.br</a>"
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "startIcon": {"knownIcon": "PHONE"},
                                        "text": "<b>Telefone:</b> (11) 3195-2299"
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "startIcon": {"knownIcon": "CLOCK"},
                                        "text": "<b>Horário:</b> 2ª à 6ª feira - das 9h às 16h30"
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "startIcon": {"knownIcon": "STAR"},
                                        "text": "<b>Site:</b> <a href=\"https://oficioeletronico.com.br\"> https://oficioeletronico.com.br</a>"
                                    }
                                }
                            ]
                        },
                        {
                            "header": "Fale Conosco",
                            "widgets": [
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Enviar E-mail",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "mailto:oficioeletronico@onr.org.br"
                                                    }
                                                }
                                            },
                                            {
                                                "text": "Acessar Site",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://oficioeletronico.com.br"
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }

def gerar_card_treinamento():
    return {
        "cardsV2": [
            {
                "cardId": "treinamentos_onr",
                "card": {
                    "header": {
                        "title": "🎓 Treinamentos ONR",
                        "subtitle": "Agende seu próximo treinamento",
                        "imageUrl": "https://www.irib.org.br/app/webroot/files/downloads/images/ONR%20logo.PNG",
                        "imageType": "SQUARE",
                        "imageAltText": "Logo ONR"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "image": {
                                        "imageUrl": "https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=400&q=80",
                                        "altText": "Treinamento ONR"
                                    }
                                },
                                {
                                    "textParagraph": {
                                        "text": (
                                            "<b>O ONR oferece treinamentos online gratuitos</b><br>"
                                            "especialmente voltados às serventias de registro<br>"
                                            "de imóveis de todo o Brasil?<br><br>"
                                            
                                            "Com o objetivo de apoiar e qualificar o atendimento<br>"
                                            "digital, a equipe de Atendimento do ONR disponibiliza<br>"
                                            "capacitações conduzidas de forma clara, prática e<br>"
                                            "ao vivo. Os conteúdos são ministrados por<br>"
                                            "profissionais que conhecem a fundo a rotina das<br>"
                                            "serventias e que atuam diariamente em apoio às<br>"
                                            "unidades do país.<br><br>"

                                            "<b>Conheça os Treinamentos Disponíveis</b><br><br>"

                                            "Atualmente, são oferecidos nove treinamentos<br>"
                                            "voltados às principais funcionalidades dos sistemas:<br><br>"

                                            "• Ofício Eletrônico<br>"
                                            "• Penhora Online<br>"
                                            "• Intimação e Consolidação SEIC<br>"
                                            "• E-intimação<br>"
                                            "• IARI<br>"
                                            "• Comunicação às Prefeituras<br>"
                                            "• CNIB para Cartórios<br>"
                                            "• CNIB para o Poder Judiciário<br>"
                                            "• Correição Online<br><br>"

                                            "Clique no botão abaixo e agende o seu treinamento."
                                        )

                                    }
                                },
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Ver Agenda de Treinamentos",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://sites.google.com/onr.org.br/onr-agendamento-de-treinamento"
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }

def card_notícias():
    return {
        "cardsV2": [
            {
                "cardId": "novidades_onr",
                "card": {
                    "header": {
                        "title": "📰 Fique por dentro das novidades!",
                        "subtitle": "Acesse as notícias e atualizações do ONR",
                        "imageUrl": "https://www.irib.org.br/app/webroot/files/downloads/images/ONR%20logo.PNG",
                        "imageType": "SQUARE",
                        "imageAltText": "Logo ONR"
                    },
                    "sections": [
                        {
                            "widgets": [
                                {
                                    "textParagraph": {
                                        "text": (
                                            "Confira as últimas notícias, comunicados e novidades do ONR.<br>"
                                            "<i>Mantenha-se informado sobre atualizações, eventos e muito mais!</i>"
                                        )
                                    }
                                },
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Ver Notícias",
                                                "onClick": {
                                                    "openLink": {
                                                        "url": "https://www.onr.org.br/noticias/"
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }

def gerar_card_plataformas():
    plataformas = [
        ("🔗 CNIB 2.0", "https://indisponibilidade.onr.org.br/"),
        ("📬 e-Intimação", "https://e-intimacao.onr.org.br/"),
        ("📄 FIC/SREI", "https://fic.srei.onr.org.br/"),
        ("🧾 IARI", "https://app.onr.org.br/login"),
        ("🗺️ MAPA", "https://mapa.onr.org.br/sigri/intranet"),
        ("📨 Ofício Eletrônico", "https://oficioeletronico.com.br/"),
        ("🔒 Penhora Online", "https://penhoraonline.org.br/"),
        ("🏛️ PGV-CNM", "https://cnm.onr.org.br/"),
        ("🌐 RI Digital", "https://ridigital.org.br/")
    ]

    widgets = [
        {
            "decoratedText": {
                "text": "<b>Explore as principais plataformas digitais disponibilizadas<br> pelo ONR para otimizar os serviços do seu cartório:</b><br><br>",
                "wrapText": True
            }
        }
    ]

    for nome, url in plataformas:
        widgets.append({
            "decoratedText": {
                "text": f"<b>{nome}</b>",
                "button": {
                    "text": "Acessar",
                    "onClick": {
                        "openLink": {"url": url}
                    }
                },
                "wrapText": False  # força manter em uma linha
            }
        })

    return {
        "cardsV2": [
            {
                "cardId": "plataformas-onr",
                "card": {
                    "header": {
                        "title": "<b>Plataformas Digitais do ONR</b>",
                        "subtitle": "Acesse os links úteis dos Cartórios de Registro de Imóveis"  # tiramos para ganhar altura
                    },
                    "sections": [
                        {
                            "widgets": widgets
                        }
                    ]
                }
            }
        ]
    }