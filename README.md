# discord-afreecatv-alert-bot
디스코드 아프리카 알리미 봇 (아프리카tv 방송알림)

2022.12.04 -> 신규 서비스로 개편되어 본 레포지토리는 아카이브 처리하겠습니다.
- https://github.com/dokdo2013/afreecatv-discord
- https://github.com/dokdo2013/afreecatv-discord-sender

## Infra
~~2022년 08월 03일 `EC2` -> `EKS` 이전~~ 다시 `EC2` 에서 운영

### [DEPRECATED]
현재는 한 명의 BJ에 대해 하나의 채널에만 알림이 가능한 형태로 개발되어 있습니다. 이걸 범용으로 활용할 수 있도록 개편하는 작업을 진행 중입니다. 해당 작업이 완료되면 본 레포지토리는 Archived 처리하고 새로운 레포지토리에서 계속 개발할 예정입니다.

### DDL
```sql
create or replace table afreeca_alert.latest_broadcast
(
    idx             int auto_increment comment '번호'
        primary key,
    user_id         varchar(50)       null comment '회원 ID',
    broad_no        varchar(20)       null comment '방송 고유 ID',
    broad_datetime  datetime          null comment '방송시작 일시',
    update_datetime datetime          null comment '업데이트 일시',
    del_stat        tinyint default 0 null comment '삭제 여부',
    del_datetime    datetime          null comment '삭제 일시',
    constraint latest_broadcast_user_id_uindex
        unique (user_id)
)
    comment '업데이트된 최신 방송';

```
