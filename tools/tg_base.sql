-- SET statement_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SET check_function_bodies = false;
-- SET client_min_messages = warning;

--TODO: add column data registration and language
CREATE TABLE users (
    user_id BIGINT UNIQUE,
    login TEXT UNIQUE,
    isAdmin BOOLEAN,
    status_user BIGINT,
    type TEXT,
    company_ai TEXT,
    model TEXT,
    speaker_name TEXT,
    contextSize BIGINT,
    language_code TEXT,
    id BIGSERIAL PRIMARY KEY
);

CREATE TABLE users (
    user_id BIGINT UNIQUE,
    login TEXT UNIQUE,

);

CREATE TABLE users_in_groups (
    user_id BIGINT UNIQUE,
    chats_id BIGINT[],
    id BIGSERIAL PRIMARY KEY
);

-- TODO: add column data , тип записи сообщения
CREATE TABLE context (
    user_id BIGINT,
    chat_id BIGINT,
    role    TEXT,
    message_id BIGINT,
    message TEXT,
    isPhoto BOOLEAN,
    id BIGSERIAL PRIMARY KEY
);


-- remove this table
CREATE TABLE admins (
    user_id BIGINT UNIQUE,
    login TEXT UNIQUE,
    status BIGINT,
    id BIGSERIAL PRIMARY KEY
);




-- CREATE TABLE statistic (
--     id BIGSERIAL PRIMARY KEY
-- );




CREATE TABLE assistant_ai (
    company_ai TEXT,
    model_name TEXT,
    description TEXT,
    token_size INT,
    last_update TEXT,
    status_lvl BIGINT,
    isView BOOLEAN,
    id BIGSERIAL PRIMARY KEY
);


CREATE TABLE voices(
    name TEXT,
    language TEXT,
    gender TEXT,
    language_code TEXT,
    id BIGSERIAL PRIMARY KEY
);

-- CREATE TABLE user_settings(
--     user_id BIGINT,

-- );




-- DROP FUNCTION add_chats_id(p_user_id BIGINT, p_chats_id BIGINT[]) 
CREATE FUNCTION add_chats_id(p_user_id BIGINT, p_chats_id BIGINT[]) 
RETURNS VOID AS $$
BEGIN
    -- Проверяем наличие записи с заданным user_id
    IF EXISTS (SELECT 1 FROM users_in_groups WHERE user_id = p_user_id) THEN
        -- Если запись существует, добавляем только уникальные значения в массив chats_id
        UPDATE users_in_groups SET chats_id = ARRAY(SELECT DISTINCT unnest(chats_id) UNION SELECT unnest(p_chats_id))
        WHERE user_id = p_user_id;
    ELSE
        -- Если записи не существует, создаем новую запись и указываем chats_id
        INSERT INTO users_in_groups (user_id, chats_id) VALUES (p_user_id, p_chats_id);
    END IF;
END;
$$ LANGUAGE plpgsql;



-- DROP FUNCTION get_chats_id(IN p_user_id BIGINT)
CREATE OR REPLACE FUNCTION get_chats_id(IN p_user_id BIGINT)
    RETURNS SETOF BIGINT[] AS
$$
BEGIN
    RETURN QUERY 
    SELECT chats_id 
    FROM users_in_groups 
    WHERE users_in_groups.user_id = p_user_id;
END;
$$
LANGUAGE plpgsql;





-- -- https://platform.openai.com/docs/models/continuous-model-upgrades

insert into assistant_ai values('OpenAi', 'gpt-3.5-turbo',          'default',  4097,   'Up to Sep 2021',   1, True);
insert into assistant_ai values('OpenAi', 'gpt-4',                  '',         8192,   'Up to Sep 2021',   1, True);
insert into assistant_ai values('OpenAi', 'gpt-4-1106-preview',     '',         128000, 'Up to Apr 2023',   2, True);
insert into assistant_ai values('OpenAi', 'gpt-4-vision-preview',   '',         128000, 'Up to Apr 2023',   2, False);
insert into assistant_ai values('Yandex', 'yandexgpt',              'yandex',   8000,   '06.12.2023',       2, False);
insert into assistant_ai values('Yandex', 'yandexgpt-lite',         'yandex',   8000,   '06.12.2023',       2, True);
insert into assistant_ai values('Sber',   'GigaChat',              'sber',     4096,   '-',                1, True);
-- -- insert into model_gpt values('', '');


-- -- https://cloud.yandex.com/en-ru/docs/speechkit/tts/voices
-- insert into voices values('dasha',  'Russian',  'F','ru-RU');
-- insert into voices values('alena',  'Russian',  'F','ru-RU');
-- insert into voices values('lea',    'German',   'F','de-DE');
-- insert into voices values('john',   'English',  'M','en-US');
-- insert into voices values('naomi',  'Hebrew',   'F','he-IL');
-- insert into voices values('amira',  'Kazakh',   'F','kk-KK');
-- insert into voices values('madi',   'Kazakh',   'M','kk-KK');
-- insert into voices values('nigora', 'Uzbek',    'F','uz-UZ');
-- -- insert into voices values('','','','');