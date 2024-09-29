--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4 (Debian 16.4-1.pgdg120+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: test_table; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_table (
    id integer NOT NULL,
    name character varying(100),
    age integer
);


--
-- Name: test_table_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.test_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: test_table_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.test_table_id_seq OWNED BY public.test_table.id;


--
-- Name: test_table id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_table ALTER COLUMN id SET DEFAULT nextval('public.test_table_id_seq'::regclass);


--
-- Data for Name: test_table; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.test_table (id, name, age) VALUES (1, 'Alice', 30);
INSERT INTO public.test_table (id, name, age) VALUES (2, 'Bob', 25);
INSERT INTO public.test_table (id, name, age) VALUES (3, 'Charlie', 35);


--
-- Name: test_table_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.test_table_id_seq', 3, true);


--
-- Name: test_table test_table_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_table
    ADD CONSTRAINT test_table_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

