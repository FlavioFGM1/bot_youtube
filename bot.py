# Import de Web Bot
from botcity.web import WebBot, Browser, By

# Import de integração com BotCity Maestro SDK
from botcity.maestro import *

from datetime import datetime

# Desativa mensagem de erros por não estar conectado ao Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False



def main():
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    bot = WebBot()

    # Configurando para rodar em modo headless
    bot.headless = False

    # Setando Firefox
    bot.browser = Browser.FIREFOX

    # Setando caminho do WebDriver
    bot.driver_path = r"resources\geckodriver.exe"

    maestro.alert(
        task_id=execution.task_id,
        title="BotYoutube - Inicio",
        message="Estamos iniciando o processo",
        alert_type=AlertType.INFO
    )

    canais = execution.parameters.get("canais", "botcity_br")

    canais = canais.split(",")

    try:
        for canal in canais:
            # Inicia o navegador
            bot.browse(f"https://www.youtube.com/@{canal}")
            # Retorna lista de elementos
            element = bot.find_elements(selector='//span[@class="yt-core-attributed-string yt-content-metadata-view-model-wiz__metadata-text yt-core-attributed-string--white-space-pre-wrap yt-core-attributed-string--link-inherit-color" and @role="text"]', by=By.XPATH)
            # Captura o texto de cada elemento
            nome_canal = element[0].text
            numero_inscritos = element[1].text
            quantidade_videos = element[2].text
            print(f"Nome do canal: {nome_canal} | Número de inscritos: {numero_inscritos} | Quantidade de vídeos: {quantidade_videos}")
            maestro.new_log_entry(
                activity_label="YouTube",
                values = {
                    "task_id": execution.task_id,
                    "data_hora": datetime.now().strftime("%Y-%m-%d_%H-%M"),
                    "canal": nome_canal,
                    "inscritos": numero_inscritos
                }
            )
            # Salvando uma captura de tela
            bot.save_screenshot("captura.png")

            # Enviando para a plataforma com o nome "Captura Canal..."
            maestro.post_artifact(
                task_id=execution.task_id,
                artifact_name=f"Captura Canal {numero_inscritos}.png",
                filepath="captura.png"
            )




        # Forçando uma exception para registrarmos um erro
        #x = 0/0

        status = AutomationTaskFinishStatus.SUCCESS
        message = "Tarefa BotYoutube finalizada com sucesso"
        
        

    except Exception as ex:
        # Salvando captura de tela do erro
        bot.save_screenshot("erro.png")
        
        print()
        print(ex)
        print()

        # Dicionario de tags adicionais
        tags = {"canal": canal}

        # Registrando o erro
        maestro.error(
            task_id=execution.task_id,
            exception=ex,
            screenshot="erro.png",
            tags=tags
        )

        status = AutomationTaskFinishStatus.FAILED
        message = "Tarefa BotYoutube finalizada com falha"

    finally:
        bot.wait(2000)
        bot.stop_browser()

        # Finalizando a tarefa
        maestro.finish_task(
            task_id=execution.task_id,
            status=status,
            message=message
        )



if __name__ == '__main__':
    main()