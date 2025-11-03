--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.0

-- Started on 2025-11-03 02:25:00 CET

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 851 (class 1247 OID 150547)
-- Name: bookingstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.bookingstatus AS ENUM (
    'PENDING',
    'CONFIRMED',
    'CHECKED_IN',
    'CHECKED_OUT',
    'CANCELLED'
);


ALTER TYPE public.bookingstatus OWNER TO postgres;

--
-- TOC entry 854 (class 1247 OID 150558)
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.paymentstatus AS ENUM (
    'PENDING',
    'COMPLETED',
    'FAILED',
    'REFUNDED'
);


ALTER TYPE public.paymentstatus OWNER TO postgres;

--
-- TOC entry 857 (class 1247 OID 150568)
-- Name: roomtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.roomtype AS ENUM (
    'SINGLE_ROOM',
    'DOUBLE_ROOM',
    'TWIN_ROOM',
    'FAMILY_ROOM',
    'SUITE_ROOM',
    'DELUXE_ROOM',
    'PRESIDENTIAL_SUITE'
);


ALTER TYPE public.roomtype OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 219 (class 1259 OID 150623)
-- Name: bookings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bookings (
    id uuid NOT NULL,
    guest_id uuid NOT NULL,
    hotel_id uuid NOT NULL,
    room_id uuid NOT NULL,
    check_in_date timestamp with time zone NOT NULL,
    check_out_date timestamp with time zone NOT NULL,
    total_price numeric(10,2) NOT NULL,
    booking_status public.bookingstatus NOT NULL,
    num_guests integer NOT NULL,
    special_requests character varying(20),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    is_active boolean NOT NULL
);


ALTER TABLE public.bookings OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 150677)
-- Name: guests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.guests (
    id uuid NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    email character varying NOT NULL,
    phone_number character varying NOT NULL,
    password character varying NOT NULL,
    address character varying,
    nationality character varying,
    passport_number character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    last_login_at timestamp with time zone,
    last_logout_at timestamp with time zone,
    session_token character varying,
    is_active boolean NOT NULL
);


ALTER TABLE public.guests OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 150589)
-- Name: hotels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hotels (
    id uuid NOT NULL,
    name character varying(100) NOT NULL,
    address character varying(200) NOT NULL,
    city character varying(100) NOT NULL,
    postal_code character varying(20),
    phone_number character varying(20),
    email character varying(100),
    total_rooms integer NOT NULL,
    star_rating numeric(10,2),
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    is_active boolean NOT NULL
);


ALTER TABLE public.hotels OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 150644)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id uuid NOT NULL,
    booking_id uuid NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_method character varying(50) NOT NULL,
    transaction_date timestamp with time zone NOT NULL,
    payment_status public.paymentstatus NOT NULL,
    transaction_reference character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    is_active boolean NOT NULL
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 150659)
-- Name: reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reviews (
    id uuid NOT NULL,
    hotel_id uuid NOT NULL,
    guest_id uuid NOT NULL,
    rating integer,
    review_text text,
    review_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    is_active boolean NOT NULL
);


ALTER TABLE public.reviews OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 150610)
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    id uuid NOT NULL,
    hotel_id uuid NOT NULL,
    room_number character varying(20) NOT NULL,
    room_type public.roomtype NOT NULL,
    price_per_night double precision NOT NULL,
    max_occupancy integer NOT NULL,
    floor integer,
    status character varying(20) NOT NULL,
    additional_notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone,
    is_active boolean NOT NULL
);


ALTER TABLE public.rooms OWNER TO postgres;

--
-- TOC entry 3453 (class 0 OID 150623)
-- Dependencies: 219
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.bookings VALUES ('bd7503b0-d49d-4948-87f7-6e0115f72b7b', 'b853d3d2-dabf-4a98-a4a2-0eda1d25c9e2', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '4fc7745e-1b27-4201-b730-ab494cf0f0a9', '2025-11-21 00:00:00+00', '2025-11-25 00:00:00+00', 380.00, 'PENDING', 1, NULL, '2025-11-02 22:39:00.147284+00', NULL, NULL, true);


--
-- TOC entry 3456 (class 0 OID 150677)
-- Dependencies: 222
-- Data for Name: guests; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.guests VALUES ('b853d3d2-dabf-4a98-a4a2-0eda1d25c9e2', 'sokheng', 'din', 'sokheng.din@gmail.com', '011226690', '$argon2id$v=19$m=65536,t=3,p=4$XMu5N0YIYQwh5HwPgdA6xw$hsn6QetyhGO3UpmCuaXkrj5znTTeErW3SM2GIZrJX1c', NULL, NULL, NULL, '2025-11-02 22:36:59.459303+00', NULL, NULL, '2025-11-02 22:37:35.45578+00', NULL, 'Yr1oD7LmloUstM5wGtrYqmmBITRslH_TRl9_QOayYnY', true);


--
-- TOC entry 3451 (class 0 OID 150589)
-- Dependencies: 217
-- Data for Name: hotels; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.hotels VALUES ('5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'Angkor Paradise Resort & Spa', 'National Road 6, Phum Kruos, Sangkat Svay Dangkum', 'Siem Reap', '17252', '+855 63 963 999', 'contact@angkorparadiseresort.com', 120, 4.80, 'A luxury resort offering elegant rooms, outdoor swimming pool, spa, and fine dining near the heart of Siem Reap and just minutes from Angkor Wat.', '2025-11-02 22:30:56.422404+00', NULL, NULL, true);


--
-- TOC entry 3454 (class 0 OID 150644)
-- Dependencies: 220
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3455 (class 0 OID 150659)
-- Dependencies: 221
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3452 (class 0 OID 150610)
-- Dependencies: 218
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.rooms VALUES ('144e548e-bd67-40b3-9298-66ab080dfc6e', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '101', 'SINGLE_ROOM', 65, 1, 1, 'AVAILABLE', 'Cozy single room with garden courtyard view.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('ac778f8b-83a4-4d90-833b-7184c572e5bc', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '102', 'DOUBLE_ROOM', 85, 2, 1, 'AVAILABLE', 'Double room with private balcony and courtyard access.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('be64f354-9da9-48f8-8081-32b7a76d49db', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '103', 'TWIN_ROOM', 80, 2, 1, 'AVAILABLE', 'Twin beds and minimalist interior design.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('5b658943-7ef7-4468-adf9-b04c383364bb', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '104', 'FAMILY_ROOM', 145, 4, 1, 'AVAILABLE', 'Family suite with two queen beds and garden access.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('07cb55c3-b978-4630-aabf-48500c1d29f3', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '105', 'DELUXE_ROOM', 160, 2, 1, 'AVAILABLE', 'Deluxe room with pool view and king-size bed.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('6a4a3a0d-261d-407f-845e-2af60fdc2024', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '106', 'SUITE_ROOM', 220, 2, 1, 'AVAILABLE', 'Luxury suite with living area and marble bathroom.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('bbb286ee-7174-4b43-99c3-0b87205600b6', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '201', 'SINGLE_ROOM', 70, 1, 2, 'AVAILABLE', 'Single room with pool view and modern decor.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('84a1df49-dd99-45e2-a043-182c969ef639', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '202', 'DOUBLE_ROOM', 95, 2, 2, 'AVAILABLE', 'Comfortable double room overlooking tropical pool.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('94c8f69c-b8fd-47f6-88c0-89c74cf2df5c', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '203', 'TWIN_ROOM', 90, 2, 2, 'AVAILABLE', 'Spacious twin room for business or leisure.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('a863dfa7-a216-4d47-bb20-1fb5844ac5bd', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '204', 'FAMILY_ROOM', 160, 4, 2, 'AVAILABLE', 'Family suite with children-friendly design and sofa bed.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('196837ca-6674-482f-9655-35e02aab09d6', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '205', 'DELUXE_ROOM', 180, 2, 2, 'AVAILABLE', 'Deluxe room with private terrace and breakfast included.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('2eb22efa-a969-43ae-9939-00c1a7bae4d8', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '206', 'SUITE_ROOM', 250, 3, 2, 'AVAILABLE', 'Suite with kitchenette and sunset view balcony.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('456ecc38-ec7a-44f2-9695-e30bc4283a6a', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '301', 'SINGLE_ROOM', 75, 1, 3, 'AVAILABLE', 'Executive single with ergonomic workspace.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('336716c9-6cd5-4203-9bef-54ef6fe7f199', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '302', 'DOUBLE_ROOM', 110, 2, 3, 'AVAILABLE', 'Executive double with high-speed Wi-Fi and minibar.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('90ef5b2a-93d6-495b-9cf1-08697683079e', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '303', 'TWIN_ROOM', 105, 2, 3, 'AVAILABLE', 'Modern twin room with balcony and desk area.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('84f80fe5-0697-4019-af76-3cc231d230c0', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '304', 'DELUXE_ROOM', 190, 2, 3, 'AVAILABLE', 'Deluxe room with pool view and high-end amenities.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('8556f5e1-0e85-478a-aac8-72024963b0ba', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '305', 'SUITE_ROOM', 260, 3, 3, 'AVAILABLE', 'Corner suite with panoramic view and private lounge.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('8a566d44-79be-43cf-af60-32db6adb4138', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '306', 'PRESIDENTIAL_SUITE', 480, 4, 3, 'AVAILABLE', 'Presidential suite with meeting area and private dining.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('e1494bcb-c4fe-40f3-ad1d-a234fdd3428a', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '401', 'SINGLE_ROOM', 85, 1, 4, 'AVAILABLE', 'Single with balcony and skyline view of Siem Reap.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('d0c0d47b-5854-4b04-b5d6-ea030d757920', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '402', 'DOUBLE_ROOM', 120, 2, 4, 'AVAILABLE', 'Romantic double room with canopy bed and terrace.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('921d1cc1-9c44-4b2d-80b3-d779f77816e4', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '403', 'TWIN_ROOM', 115, 2, 4, 'AVAILABLE', 'Twin beds with scenic view and reading lights.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('dc07b342-f270-4014-b41a-3c25e55d57be', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '404', 'FAMILY_ROOM', 175, 4, 4, 'AVAILABLE', 'Spacious family suite with two bathrooms.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('014a231f-f19e-48bf-8dd1-2001100ae01a', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '405', 'DELUXE_ROOM', 210, 2, 4, 'AVAILABLE', 'Deluxe with king bed, balcony, and espresso machine.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('9c25908c-57e2-4729-aa78-bf9db274e201', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '406', 'SUITE_ROOM', 290, 3, 4, 'AVAILABLE', 'Suite with separate dining and entertainment area.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('2f74910b-0438-4aab-8046-5d5384ff5037', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '407', 'PRESIDENTIAL_SUITE', 520, 4, 4, 'AVAILABLE', 'Presidential suite with private jacuzzi and butler service.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('65b745b7-353a-43d0-9a8d-414c5eec1fa2', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '501', 'SINGLE_ROOM', 90, 1, 5, 'AVAILABLE', 'Top-floor single room with best sunrise view.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('9796ad1d-fd8f-4c63-9df1-e2e10e0be15d', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '502', 'DOUBLE_ROOM', 130, 2, 5, 'AVAILABLE', 'Romantic double suite with jacuzzi bath.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('364b9ed9-2af4-4933-8433-440678e4ae7f', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '503', 'TWIN_ROOM', 120, 2, 5, 'AVAILABLE', 'Twin with skyline view and private balcony.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('a6c30177-8bd8-4dd4-87a8-e120f10908ed', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '504', 'FAMILY_ROOM', 190, 4, 5, 'AVAILABLE', 'Family suite with kitchenette and sofa lounge.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('f4456d41-58d1-403d-afd1-039a3ac47cec', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '505', 'DELUXE_ROOM', 230, 2, 5, 'AVAILABLE', 'Deluxe with private jacuzzi and soundproof walls.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('1869df9b-639d-4106-9c52-241fa61fd786', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '506', 'SUITE_ROOM', 310, 3, 5, 'AVAILABLE', 'Royal suite with panoramic Angkor skyline view.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('80334de3-d962-420e-bc4d-38457541348e', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', '507', 'PRESIDENTIAL_SUITE', 600, 4, 5, 'AVAILABLE', 'Presidential Sky Villa with private pool and terrace.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('809e7721-ddda-4159-8fe8-d5944e15f9f1', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'G01', 'DOUBLE_ROOM', 95, 2, 0, 'AVAILABLE', 'Ground-floor double with garden patio and pool access.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('032eac51-9de8-4fc5-83fb-0fefa733dbb9', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'G02', 'TWIN_ROOM', 90, 2, 0, 'AVAILABLE', 'Twin with private terrace facing tropical gardens.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('81efa13d-afa4-44fc-990b-ff8800a01bf6', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'G03', 'FAMILY_ROOM', 160, 4, 0, 'AVAILABLE', 'Family suite directly connected to children’s playground.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('14320a51-7871-41ac-a5e5-18092419d063', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'G04', 'DELUXE_ROOM', 175, 2, 0, 'AVAILABLE', 'Deluxe with pool access and sun loungers.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('4fc7745e-1b27-4201-b730-ab494cf0f0a9', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'E01', 'SINGLE_ROOM', 95, 1, 6, 'AVAILABLE', 'Single executive room with smart lighting and desk.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('4dbd16c7-3480-4ba8-9a55-85b9bafb940b', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'E02', 'DOUBLE_ROOM', 135, 2, 6, 'AVAILABLE', 'Executive double with smart TV and high-end finish.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('91d94ec0-8c68-40ee-b2f7-52d67025c8db', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'E03', 'DELUXE_ROOM', 220, 2, 6, 'AVAILABLE', 'Executive deluxe with rain shower and sofa.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('32c7a7c5-2f88-4985-af0c-aa8b23252db5', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'E04', 'SUITE_ROOM', 330, 3, 6, 'AVAILABLE', 'Executive suite with business lounge access.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('85f384ff-2fc4-4a93-a009-4a39f8626dfe', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'E05', 'PRESIDENTIAL_SUITE', 650, 4, 6, 'AVAILABLE', 'Top-tier executive presidential suite with concierge service.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('f9052f8c-3aa0-46b7-8f55-7ba4bfa2ec4c', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'PH1', 'SUITE_ROOM', 700, 3, 7, 'AVAILABLE', 'Sky suite with private infinity pool and rooftop garden.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);
INSERT INTO public.rooms VALUES ('62d8a599-248f-401d-bd2b-20722ba1737e', '5d6926a8-1100-4d8c-a8ed-d7351e0cd121', 'PH2', 'PRESIDENTIAL_SUITE', 950, 5, 7, 'AVAILABLE', 'Presidential penthouse with panoramic 360° city view and butler.', '2025-11-02 22:33:48.968484+00', NULL, NULL, true);


--
-- TOC entry 3292 (class 2606 OID 150628)
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);


--
-- TOC entry 3298 (class 2606 OID 150686)
-- Name: guests guests_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guests
    ADD CONSTRAINT guests_email_key UNIQUE (email);


--
-- TOC entry 3300 (class 2606 OID 150684)
-- Name: guests guests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.guests
    ADD CONSTRAINT guests_pkey PRIMARY KEY (id);


--
-- TOC entry 3288 (class 2606 OID 150596)
-- Name: hotels hotels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hotels
    ADD CONSTRAINT hotels_pkey PRIMARY KEY (id);


--
-- TOC entry 3294 (class 2606 OID 150649)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- TOC entry 3296 (class 2606 OID 150666)
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- TOC entry 3290 (class 2606 OID 150617)
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- TOC entry 3302 (class 2606 OID 150634)
-- Name: bookings bookings_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id);


--
-- TOC entry 3303 (class 2606 OID 150639)
-- Name: bookings bookings_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id);


--
-- TOC entry 3304 (class 2606 OID 150650)
-- Name: payments payments_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id);


--
-- TOC entry 3305 (class 2606 OID 150667)
-- Name: reviews reviews_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id);


--
-- TOC entry 3301 (class 2606 OID 150618)
-- Name: rooms rooms_hotel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_hotel_id_fkey FOREIGN KEY (hotel_id) REFERENCES public.hotels(id);


-- Completed on 2025-11-03 02:25:00 CET

--
-- PostgreSQL database dump complete
--

