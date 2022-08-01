from logging.config import dictConfig
import logging
import discord
from discord.ext import tasks, commands
import dotenv
import os
import broadcast


def load_environment():
    if not os.path.isfile('.env'):  # 먼저 .env file 존재 여부 확인
        return {
            'isSuccess': False,
            'data': '환경변수 파일이 존재하지 않습니다.'
        }
    else:
        dotenv.load_dotenv()  # .env 로드
        return {
            'isSuccess': True
        }


gm = discord.Game('!도움말')
app = commands.Bot(command_prefix='!', activity=gm)

@app.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(app.user.name)
    print('connection was succesful')
    await app.change_presence(status=discord.Status.online, activity=gm)


@app.command()
async def 도움말(ctx):
    await ctx.send('아프리카TV 생방송 알림봇입니다. (hami0825 전용)')

@tasks.loop(seconds=20.0)
async def loop():
    user_id = os.environ.get('USER_ID')
    try:
        # broadcast 데이터 받아오기
        api_data = broadcast.get_broadcast_info(user_id)
        if not api_data["user_exist"]:
            logging.info(f'User not broadcasting : {user_id}')
            return False
        elif not api_data['on_air']:
            logging.info(f'User not broadcasting : {user_id}')
            return False

        # is_latest_broadcast가 True일 때 최신으로 Update하고 Alert 보내기
        if broadcast.is_latest_broadcast(user_id, api_data['broadcast_data']['broad_no']):
            logging.info(f'User now broadcasting!! : {user_id}')
            broadcast.set_latest_broadcast(user_id, api_data['broadcast_data']['broad_no'], api_data['broadcast_data']['broad_datetime'])

            # Make Embed
            embed_title = api_data['user_data']['user_nick']
            embed_description = "{}님이 방송을 켰습니다!  https://play.afreecatv.com/{}/{}".format(api_data['user_data']['user_nick'], api_data['user_data']['user_id'], api_data['broadcast_data']['broad_no'])
            embed_thumbnail = 'https:' + api_data['user_data']['profile_image']
            embed_image = 'https://liveimg.afreecatv.com/h/' + str(api_data['broadcast_data']['broad_no']) + '.webp'
            embed_data = discord.Embed(title=embed_title, description=embed_description)
            embed_data.set_thumbnail(url=embed_thumbnail)
            embed_data.set_image(url=embed_image)

            # Send Message
            channel = app.get_channel(int(os.environ.get('CHANNEL')))
            await channel.send('@everyone')
            await channel.send(embed=embed_data)
        else:
            logging.info(f'Already latest broadcast : {user_id}')
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    # Logger 기본 설정
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s|%(lineno)d|%(funcName)s|%(levelname)s] %(message)s'
            }
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': 'afreecatv_alert_log.log',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['file']
        }
    })

    keys = os.environ.keys()

    for item in keys:
        print("%s=%s" % (item, os.environ[item]))

    load_environment()
    loop.start()
    app.run(os.environ.get('APP_TOKEN'))

