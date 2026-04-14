def get_templates():
    return [
    {
        "id": "template_small",
        "name": "Static Blog (Small - 4 nodes)",
        "description": "Basic global static site hosting pipeline.",
        "graph": {
            "nodes": {
                "client_1": {
                    "label": "Global Users",
                    "type": "client",
                    "base_rps": 500,
                    "position": {
                        "x": 100,
                        "y": 200
                    }
                },
                "dns_1": {
                    "label": "Route53",
                    "type": "dns",
                    "capacity": 50000,
                    "position": {
                        "x": 350,
                        "y": 200
                    }
                },
                "cdn_1": {
                    "label": "CloudFront CDN",
                    "type": "cdn",
                    "capacity": 20000,
                    "position": {
                        "x": 600,
                        "y": 200
                    }
                },
                "obj_1": {
                    "label": "S3 Content",
                    "type": "object_store",
                    "capacity": 1000,
                    "position": {
                        "x": 850,
                        "y": 200
                    }
                }
            },
            "edges": [
                {
                    "source": "client_1",
                    "target": "dns_1"
                },
                {
                    "source": "dns_1",
                    "target": "cdn_1"
                },
                {
                    "source": "cdn_1",
                    "target": "obj_1"
                }
            ]
        }
    },
    {
        "id": "template_medium_ecom",
        "name": "E-commerce (Medium - 8 nodes)",
        "description": "Standard checkout architecture.",
        "graph": {
            "nodes": {
                "client_1": {
                    "label": "Shoppers",
                    "type": "client",
                    "base_rps": 1500,
                    "position": {
                        "x": 100,
                        "y": 250
                    }
                },
                "dns_1": {
                    "label": "DNS Entry",
                    "type": "dns",
                    "capacity": 50000,
                    "position": {
                        "x": 300,
                        "y": 250
                    }
                },
                "waf_1": {
                    "label": "WAF & Security",
                    "type": "load_balancer",
                    "capacity": 10000,
                    "position": {
                        "x": 500,
                        "y": 250
                    }
                },
                "alb_1": {
                    "label": "Core Gateway",
                    "type": "load_balancer",
                    "capacity": 6000,
                    "position": {
                        "x": 700,
                        "y": 250
                    }
                },
                "api_web": {
                    "label": "Frontend API",
                    "type": "api_server",
                    "capacity": 2000,
                    "position": {
                        "x": 900,
                        "y": 150
                    }
                },
                "api_pay": {
                    "label": "Payment API",
                    "type": "api_server",
                    "capacity": 800,
                    "position": {
                        "x": 900,
                        "y": 350
                    }
                },
                "cache_1": {
                    "label": "Session Cache",
                    "type": "cache",
                    "capacity": 5000,
                    "position": {
                        "x": 1150,
                        "y": 150
                    }
                },
                "db_1": {
                    "label": "Transactions DB",
                    "type": "database",
                    "write_capacity": 1000,
                    "position": {
                        "x": 1150,
                        "y": 350
                    }
                }
            },
            "edges": [
                {
                    "source": "client_1",
                    "target": "dns_1"
                },
                {
                    "source": "dns_1",
                    "target": "waf_1"
                },
                {
                    "source": "waf_1",
                    "target": "alb_1"
                },
                {
                    "source": "alb_1",
                    "target": "api_web"
                },
                {
                    "source": "alb_1",
                    "target": "api_pay"
                },
                {
                    "source": "api_web",
                    "target": "cache_1"
                },
                {
                    "source": "api_pay",
                    "target": "db_1"
                }
            ]
        }
    },
    {
        "id": "template_medium_chat",
        "name": "PubSub Chat (Medium - 8 nodes)",
        "description": "Real-time socket communication.",
        "graph": {
            "nodes": {
                "client_1": {
                    "label": "Mobile Users",
                    "type": "client",
                    "base_rps": 2500,
                    "position": {
                        "x": 50,
                        "y": 250
                    }
                },
                "alb_1": {
                    "label": "Ingress LB",
                    "type": "load_balancer",
                    "capacity": 15000,
                    "position": {
                        "x": 250,
                        "y": 250
                    }
                },
                "api_auth": {
                    "label": "Auth API",
                    "type": "api_server",
                    "capacity": 3000,
                    "position": {
                        "x": 450,
                        "y": 150
                    }
                },
                "api_soc": {
                    "label": "Socket Node",
                    "type": "api_server",
                    "capacity": 5000,
                    "position": {
                        "x": 450,
                        "y": 350
                    }
                },
                "mq_1": {
                    "label": "Kafka Broker",
                    "type": "message_queue",
                    "capacity": 20000,
                    "position": {
                        "x": 700,
                        "y": 350
                    }
                },
                "work_1": {
                    "label": "Delivery Worker",
                    "type": "worker",
                    "capacity": 2000,
                    "position": {
                        "x": 950,
                        "y": 250
                    }
                },
                "cache_1": {
                    "label": "Presence Redis",
                    "type": "cache",
                    "capacity": 8000,
                    "position": {
                        "x": 700,
                        "y": 150
                    }
                },
                "db_1": {
                    "label": "Messages DB",
                    "type": "database",
                    "write_capacity": 1500,
                    "position": {
                        "x": 1200,
                        "y": 250
                    }
                }
            },
            "edges": [
                {
                    "source": "client_1",
                    "target": "alb_1"
                },
                {
                    "source": "alb_1",
                    "target": "api_auth"
                },
                {
                    "source": "alb_1",
                    "target": "api_soc"
                },
                {
                    "source": "api_auth",
                    "target": "cache_1"
                },
                {
                    "source": "api_soc",
                    "target": "mq_1"
                },
                {
                    "source": "mq_1",
                    "target": "work_1"
                },
                {
                    "source": "work_1",
                    "target": "db_1"
                }
            ]
        }
    },
    {
        "id": "template_dense_media",
        "name": "Global Media (Dense - 12 nodes)",
        "description": "High read-throughput platform.",
        "graph": {
            "nodes": {
                "c_mob": {
                    "label": "Mobile App",
                    "type": "client",
                    "base_rps": 6000,
                    "position": {
                        "x": 50,
                        "y": 150
                    }
                },
                "c_web": {
                    "label": "Web Browsers",
                    "type": "client",
                    "base_rps": 4000,
                    "position": {
                        "x": 50,
                        "y": 350
                    }
                },
                "dns_1": {
                    "label": "Global DNS",
                    "type": "dns",
                    "capacity": 50000,
                    "position": {
                        "x": 250,
                        "y": 250
                    }
                },
                "cdn_eu": {
                    "label": "EU Edge CDN",
                    "type": "cdn",
                    "capacity": 15000,
                    "position": {
                        "x": 450,
                        "y": 150
                    }
                },
                "cdn_us": {
                    "label": "US Edge CDN",
                    "type": "cdn",
                    "capacity": 20000,
                    "position": {
                        "x": 450,
                        "y": 350
                    }
                },
                "lb_origin": {
                    "label": "Origin ALB",
                    "type": "load_balancer",
                    "capacity": 8000,
                    "position": {
                        "x": 650,
                        "y": 250
                    }
                },
                "api_vid": {
                    "label": "Video Router API",
                    "type": "api_server",
                    "capacity": 2000,
                    "position": {
                        "x": 850,
                        "y": 150
                    }
                },
                "api_usr": {
                    "label": "User Info API",
                    "type": "api_server",
                    "capacity": 1500,
                    "position": {
                        "x": 850,
                        "y": 350
                    }
                },
                "cache_l1": {
                    "label": "L1 Redis",
                    "type": "cache",
                    "capacity": 10000,
                    "position": {
                        "x": 1050,
                        "y": 50
                    }
                },
                "cache_l2": {
                    "label": "L2 Memcache",
                    "type": "cache",
                    "capacity": 8000,
                    "position": {
                        "x": 1050,
                        "y": 250
                    }
                },
                "s3_cold": {
                    "label": "Blob Storage",
                    "type": "object_store",
                    "capacity": 3000,
                    "position": {
                        "x": 1250,
                        "y": 150
                    }
                },
                "db_meta": {
                    "label": "User DB Primary",
                    "type": "database",
                    "write_capacity": 1000,
                    "position": {
                        "x": 1050,
                        "y": 450
                    }
                }
            },
            "edges": [
                {
                    "source": "c_mob",
                    "target": "dns_1"
                },
                {
                    "source": "c_web",
                    "target": "dns_1"
                },
                {
                    "source": "dns_1",
                    "target": "cdn_eu"
                },
                {
                    "source": "dns_1",
                    "target": "cdn_us"
                },
                {
                    "source": "cdn_eu",
                    "target": "lb_origin"
                },
                {
                    "source": "cdn_us",
                    "target": "lb_origin"
                },
                {
                    "source": "lb_origin",
                    "target": "api_vid"
                },
                {
                    "source": "lb_origin",
                    "target": "api_usr"
                },
                {
                    "source": "api_vid",
                    "target": "cache_l1"
                },
                {
                    "source": "cache_l1",
                    "target": "cache_l2"
                },
                {
                    "source": "cache_l2",
                    "target": "s3_cold"
                },
                {
                    "source": "api_usr",
                    "target": "db_meta"
                }
            ]
        }
    },
    {
        "id": "template_extreme_fintech",
        "name": "Global FinTech (Extreme - 20 nodes)",
        "description": "Massive scale microservices architecture.",
        "graph": {
            "nodes": {
                "c_mob": {
                    "label": "Mobile Apps",
                    "type": "client",
                    "base_rps": 2000,
                    "position": {
                        "x": 50,
                        "y": 150
                    }
                },
                "c_web": {
                    "label": "Web Portal",
                    "type": "client",
                    "base_rps": 1500,
                    "position": {
                        "x": 50,
                        "y": 300
                    }
                },
                "c_b2b": {
                    "label": "B2B API Partners",
                    "type": "client",
                    "base_rps": 800,
                    "position": {
                        "x": 50,
                        "y": 450
                    }
                },
                "dns": {
                    "label": "Global DNS",
                    "type": "dns",
                    "capacity": 100000,
                    "position": {
                        "x": 250,
                        "y": 300
                    }
                },
                "cdn": {
                    "label": "Edge Accelerator",
                    "type": "cdn",
                    "capacity": 50000,
                    "position": {
                        "x": 450,
                        "y": 225
                    }
                },
                "waf": {
                    "label": "DDoS Shield",
                    "type": "load_balancer",
                    "capacity": 30000,
                    "position": {
                        "x": 450,
                        "y": 375
                    }
                },
                "api_gw": {
                    "label": "API Gateway",
                    "type": "api_server",
                    "capacity": 15000,
                    "position": {
                        "x": 650,
                        "y": 300
                    }
                },
                "auth_svc": {
                    "label": "Auth Service",
                    "type": "serverless",
                    "capacity": 5000,
                    "position": {
                        "x": 850,
                        "y": 100
                    }
                },
                "ledger_svc": {
                    "label": "Ledger Service",
                    "type": "api_server",
                    "capacity": 3000,
                    "position": {
                        "x": 850,
                        "y": 300
                    }
                },
                "trade_svc": {
                    "label": "Trading Engine",
                    "type": "api_server",
                    "capacity": 1500,
                    "position": {
                        "x": 850,
                        "y": 500
                    }
                },
                "report_svc": {
                    "label": "Report Service",
                    "type": "serverless",
                    "capacity": 2000,
                    "position": {
                        "x": 850,
                        "y": 700
                    }
                },
                "cache_auth": {
                    "label": "Session Redis",
                    "type": "cache",
                    "capacity": 15000,
                    "position": {
                        "x": 1050,
                        "y": 100
                    }
                },
                "mq_trades": {
                    "label": "Kafka Trades",
                    "type": "message_queue",
                    "capacity": 25000,
                    "position": {
                        "x": 1050,
                        "y": 500
                    }
                },
                "work_match": {
                    "label": "Matcher Worker",
                    "type": "worker",
                    "capacity": 800,
                    "position": {
                        "x": 1250,
                        "y": 400
                    }
                },
                "work_risk": {
                    "label": "Risk Analyzer",
                    "type": "worker",
                    "capacity": 500,
                    "position": {
                        "x": 1250,
                        "y": 500
                    }
                },
                "work_audit": {
                    "label": "Audit Crawler",
                    "type": "worker",
                    "capacity": 600,
                    "position": {
                        "x": 1250,
                        "y": 600
                    }
                },
                "db_ledger": {
                    "label": "Hot Ledger DB",
                    "type": "database",
                    "write_capacity": 5000,
                    "position": {
                        "x": 1500,
                        "y": 300
                    }
                },
                "db_trades": {
                    "label": "Raw Trades DB",
                    "type": "database",
                    "write_capacity": 3000,
                    "position": {
                        "x": 1500,
                        "y": 500
                    }
                },
                "db_archive": {
                    "label": "Slow Archive DB",
                    "type": "database",
                    "write_capacity": 500,
                    "position": {
                        "x": 1500,
                        "y": 700
                    }
                },
                "s3_blob": {
                    "label": "Statement Blob",
                    "type": "object_store",
                    "capacity": 2000,
                    "position": {
                        "x": 1250,
                        "y": 700
                    }
                }
            },
            "edges": [
                {
                    "source": "c_mob",
                    "target": "dns"
                },
                {
                    "source": "c_web",
                    "target": "dns"
                },
                {
                    "source": "c_b2b",
                    "target": "dns"
                },
                {
                    "source": "dns",
                    "target": "cdn"
                },
                {
                    "source": "dns",
                    "target": "waf"
                },
                {
                    "source": "cdn",
                    "target": "api_gw"
                },
                {
                    "source": "waf",
                    "target": "api_gw"
                },
                {
                    "source": "api_gw",
                    "target": "auth_svc"
                },
                {
                    "source": "api_gw",
                    "target": "ledger_svc"
                },
                {
                    "source": "api_gw",
                    "target": "trade_svc"
                },
                {
                    "source": "api_gw",
                    "target": "report_svc"
                },
                {
                    "source": "auth_svc",
                    "target": "cache_auth"
                },
                {
                    "source": "ledger_svc",
                    "target": "db_ledger"
                },
                {
                    "source": "trade_svc",
                    "target": "mq_trades"
                },
                {
                    "source": "mq_trades",
                    "target": "work_match"
                },
                {
                    "source": "mq_trades",
                    "target": "work_risk"
                },
                {
                    "source": "mq_trades",
                    "target": "work_audit"
                },
                {
                    "source": "work_match",
                    "target": "db_ledger"
                },
                {
                    "source": "work_match",
                    "target": "db_trades"
                },
                {
                    "source": "work_risk",
                    "target": "db_trades"
                },
                {
                    "source": "work_audit",
                    "target": "db_archive"
                },
                {
                    "source": "report_svc",
                    "target": "db_archive"
                },
                {
                    "source": "report_svc",
                    "target": "s3_blob"
                }
            ]
        }
    },
    {
        "id": "template_legendary_titan",
        "name": "Global VOD Network (Legendary - 52 nodes)",
        "description": "Netflix/YouTube style architecture with geo-CDN failover and massively scalable microservices.",
        "graph": {
            "nodes": {
                "client_US_EAST": {
                    "label": "US_EAST Users",
                    "type": "client",
                    "base_rps": 12000,
                    "position": {
                        "x": 100,
                        "y": 100
                    }
                },
                "dns_US_EAST": {
                    "label": "US_EAST Route53",
                    "type": "dns",
                    "capacity": 100000,
                    "position": {
                        "x": 250,
                        "y": 100
                    }
                },
                "cdn_US_EAST_1": {
                    "label": "US_EAST Edge A",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 50
                    }
                },
                "cdn_US_EAST_2": {
                    "label": "US_EAST Edge B",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 150
                    }
                },
                "alb_US_EAST": {
                    "label": "US_EAST Gateway ALB",
                    "type": "load_balancer",
                    "capacity": 30000,
                    "position": {
                        "x": 650,
                        "y": 100
                    }
                },
                "cache_l2_US_EAST": {
                    "label": "US_EAST L2 Redis",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 850,
                        "y": 50
                    }
                },
                "api_core_US_EAST": {
                    "label": "US_EAST Core API",
                    "type": "api_server",
                    "capacity": 15000,
                    "position": {
                        "x": 850,
                        "y": 150
                    }
                },
                "client_US_WEST": {
                    "label": "US_WEST Users",
                    "type": "client",
                    "base_rps": 12000,
                    "position": {
                        "x": 100,
                        "y": 300
                    }
                },
                "dns_US_WEST": {
                    "label": "US_WEST Route53",
                    "type": "dns",
                    "capacity": 100000,
                    "position": {
                        "x": 250,
                        "y": 300
                    }
                },
                "cdn_US_WEST_1": {
                    "label": "US_WEST Edge A",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 250
                    }
                },
                "cdn_US_WEST_2": {
                    "label": "US_WEST Edge B",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 350
                    }
                },
                "alb_US_WEST": {
                    "label": "US_WEST Gateway ALB",
                    "type": "load_balancer",
                    "capacity": 30000,
                    "position": {
                        "x": 650,
                        "y": 300
                    }
                },
                "cache_l2_US_WEST": {
                    "label": "US_WEST L2 Redis",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 850,
                        "y": 250
                    }
                },
                "api_core_US_WEST": {
                    "label": "US_WEST Core API",
                    "type": "api_server",
                    "capacity": 15000,
                    "position": {
                        "x": 850,
                        "y": 350
                    }
                },
                "client_EU": {
                    "label": "EU Users",
                    "type": "client",
                    "base_rps": 12000,
                    "position": {
                        "x": 100,
                        "y": 500
                    }
                },
                "dns_EU": {
                    "label": "EU Route53",
                    "type": "dns",
                    "capacity": 100000,
                    "position": {
                        "x": 250,
                        "y": 500
                    }
                },
                "cdn_EU_1": {
                    "label": "EU Edge A",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 450
                    }
                },
                "cdn_EU_2": {
                    "label": "EU Edge B",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 550
                    }
                },
                "alb_EU": {
                    "label": "EU Gateway ALB",
                    "type": "load_balancer",
                    "capacity": 30000,
                    "position": {
                        "x": 650,
                        "y": 500
                    }
                },
                "cache_l2_EU": {
                    "label": "EU L2 Redis",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 850,
                        "y": 450
                    }
                },
                "api_core_EU": {
                    "label": "EU Core API",
                    "type": "api_server",
                    "capacity": 15000,
                    "position": {
                        "x": 850,
                        "y": 550
                    }
                },
                "client_ASIA": {
                    "label": "ASIA Users",
                    "type": "client",
                    "base_rps": 12000,
                    "position": {
                        "x": 100,
                        "y": 700
                    }
                },
                "dns_ASIA": {
                    "label": "ASIA Route53",
                    "type": "dns",
                    "capacity": 100000,
                    "position": {
                        "x": 250,
                        "y": 700
                    }
                },
                "cdn_ASIA_1": {
                    "label": "ASIA Edge A",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 650
                    }
                },
                "cdn_ASIA_2": {
                    "label": "ASIA Edge B",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 750
                    }
                },
                "alb_ASIA": {
                    "label": "ASIA Gateway ALB",
                    "type": "load_balancer",
                    "capacity": 30000,
                    "position": {
                        "x": 650,
                        "y": 700
                    }
                },
                "cache_l2_ASIA": {
                    "label": "ASIA L2 Redis",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 850,
                        "y": 650
                    }
                },
                "api_core_ASIA": {
                    "label": "ASIA Core API",
                    "type": "api_server",
                    "capacity": 15000,
                    "position": {
                        "x": 850,
                        "y": 750
                    }
                },
                "client_SA": {
                    "label": "SA Users",
                    "type": "client",
                    "base_rps": 12000,
                    "position": {
                        "x": 100,
                        "y": 900
                    }
                },
                "dns_SA": {
                    "label": "SA Route53",
                    "type": "dns",
                    "capacity": 100000,
                    "position": {
                        "x": 250,
                        "y": 900
                    }
                },
                "cdn_SA_1": {
                    "label": "SA Edge A",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 850
                    }
                },
                "cdn_SA_2": {
                    "label": "SA Edge B",
                    "type": "cdn",
                    "capacity": 25000,
                    "position": {
                        "x": 450,
                        "y": 950
                    }
                },
                "alb_SA": {
                    "label": "SA Gateway ALB",
                    "type": "load_balancer",
                    "capacity": 30000,
                    "position": {
                        "x": 650,
                        "y": 900
                    }
                },
                "cache_l2_SA": {
                    "label": "SA L2 Redis",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 850,
                        "y": 850
                    }
                },
                "api_core_SA": {
                    "label": "SA Core API",
                    "type": "api_server",
                    "capacity": 15000,
                    "position": {
                        "x": 850,
                        "y": 950
                    }
                },
                "auth_lb": {
                    "label": "Auth Internal LB",
                    "type": "load_balancer",
                    "capacity": 50000,
                    "position": {
                        "x": 1100,
                        "y": 200
                    }
                },
                "auth_svc_0": {
                    "label": "Auth K8s Pod 0",
                    "type": "serverless",
                    "capacity": 10000,
                    "position": {
                        "x": 1300,
                        "y": 100
                    }
                },
                "auth_svc_1": {
                    "label": "Auth K8s Pod 1",
                    "type": "serverless",
                    "capacity": 10000,
                    "position": {
                        "x": 1300,
                        "y": 150
                    }
                },
                "auth_svc_2": {
                    "label": "Auth K8s Pod 2",
                    "type": "serverless",
                    "capacity": 10000,
                    "position": {
                        "x": 1300,
                        "y": 200
                    }
                },
                "auth_svc_3": {
                    "label": "Auth K8s Pod 3",
                    "type": "serverless",
                    "capacity": 10000,
                    "position": {
                        "x": 1300,
                        "y": 250
                    }
                },
                "auth_svc_4": {
                    "label": "Auth K8s Pod 4",
                    "type": "serverless",
                    "capacity": 10000,
                    "position": {
                        "x": 1300,
                        "y": 300
                    }
                },
                "db_auth_master": {
                    "label": "User DB Primary",
                    "type": "database",
                    "write_capacity": 15000,
                    "position": {
                        "x": 1500,
                        "y": 200
                    }
                },
                "db_auth_replica_1": {
                    "label": "User DB Rep1",
                    "type": "database",
                    "write_capacity": 10000,
                    "position": {
                        "x": 1650,
                        "y": 150
                    }
                },
                "db_auth_replica_2": {
                    "label": "User DB Rep2",
                    "type": "database",
                    "write_capacity": 10000,
                    "position": {
                        "x": 1650,
                        "y": 250
                    }
                },
                "catalog_lb": {
                    "label": "Catalog Mesh",
                    "type": "load_balancer",
                    "capacity": 60000,
                    "position": {
                        "x": 1100,
                        "y": 600
                    }
                },
                "cat_svc_0": {
                    "label": "Catalog Node 0",
                    "type": "api_server",
                    "capacity": 12000,
                    "position": {
                        "x": 1300,
                        "y": 500
                    }
                },
                "cat_svc_1": {
                    "label": "Catalog Node 1",
                    "type": "api_server",
                    "capacity": 12000,
                    "position": {
                        "x": 1300,
                        "y": 550
                    }
                },
                "cat_svc_2": {
                    "label": "Catalog Node 2",
                    "type": "api_server",
                    "capacity": 12000,
                    "position": {
                        "x": 1300,
                        "y": 600
                    }
                },
                "cat_svc_3": {
                    "label": "Catalog Node 3",
                    "type": "api_server",
                    "capacity": 12000,
                    "position": {
                        "x": 1300,
                        "y": 650
                    }
                },
                "cat_svc_4": {
                    "label": "Catalog Node 4",
                    "type": "api_server",
                    "capacity": 12000,
                    "position": {
                        "x": 1300,
                        "y": 700
                    }
                },
                "cat_svc_5": {
                    "label": "Catalog Node 5",
                    "type": "api_server",
                    "capacity": 12000,
                    "position": {
                        "x": 1300,
                        "y": 750
                    }
                },
                "cache_global_cat": {
                    "label": "Global Memcached",
                    "type": "cache",
                    "capacity": 80000,
                    "position": {
                        "x": 1500,
                        "y": 650
                    }
                },
                "db_catalog": {
                    "label": "Catalog DB Ring",
                    "type": "database",
                    "write_capacity": 30000,
                    "position": {
                        "x": 1700,
                        "y": 650
                    }
                },
                "media_mq": {
                    "label": "Transcode Queue",
                    "type": "message_queue",
                    "capacity": 40000,
                    "position": {
                        "x": 900,
                        "y": 900
                    }
                },
                "encoder_0": {
                    "label": "GPU Encoder 0",
                    "type": "worker",
                    "capacity": 5000,
                    "position": {
                        "x": 1100,
                        "y": 800
                    }
                },
                "encoder_1": {
                    "label": "GPU Encoder 1",
                    "type": "worker",
                    "capacity": 5000,
                    "position": {
                        "x": 1100,
                        "y": 850
                    }
                },
                "encoder_2": {
                    "label": "GPU Encoder 2",
                    "type": "worker",
                    "capacity": 5000,
                    "position": {
                        "x": 1100,
                        "y": 900
                    }
                },
                "encoder_3": {
                    "label": "GPU Encoder 3",
                    "type": "worker",
                    "capacity": 5000,
                    "position": {
                        "x": 1100,
                        "y": 950
                    }
                },
                "encoder_4": {
                    "label": "GPU Encoder 4",
                    "type": "worker",
                    "capacity": 5000,
                    "position": {
                        "x": 1100,
                        "y": 1000
                    }
                },
                "encoder_5": {
                    "label": "GPU Encoder 5",
                    "type": "worker",
                    "capacity": 5000,
                    "position": {
                        "x": 1100,
                        "y": 1050
                    }
                },
                "encoder_6": {
                    "label": "GPU Encoder 6",
                    "type": "worker",
                    "capacity": 5000,
                    "position": {
                        "x": 1100,
                        "y": 1100
                    }
                },
                "encoder_7": {
                    "label": "GPU Encoder 7",
                    "type": "worker",
                    "capacity": 5000,
                    "position": {
                        "x": 1100,
                        "y": 1150
                    }
                },
                "s3_archive": {
                    "label": "Cold Video Archive",
                    "type": "object_store",
                    "capacity": 50000,
                    "position": {
                        "x": 1350,
                        "y": 1000
                    }
                }
            },
            "edges": [
                {
                    "source": "client_US_EAST",
                    "target": "dns_US_EAST"
                },
                {
                    "source": "dns_US_EAST",
                    "target": "cdn_US_EAST_1"
                },
                {
                    "source": "dns_US_EAST",
                    "target": "cdn_US_EAST_2"
                },
                {
                    "source": "cdn_US_EAST_1",
                    "target": "alb_US_EAST"
                },
                {
                    "source": "cdn_US_EAST_2",
                    "target": "alb_US_EAST"
                },
                {
                    "source": "alb_US_EAST",
                    "target": "cache_l2_US_EAST"
                },
                {
                    "source": "alb_US_EAST",
                    "target": "api_core_US_EAST"
                },
                {
                    "source": "client_US_WEST",
                    "target": "dns_US_WEST"
                },
                {
                    "source": "dns_US_WEST",
                    "target": "cdn_US_WEST_1"
                },
                {
                    "source": "dns_US_WEST",
                    "target": "cdn_US_WEST_2"
                },
                {
                    "source": "cdn_US_WEST_1",
                    "target": "alb_US_WEST"
                },
                {
                    "source": "cdn_US_WEST_2",
                    "target": "alb_US_WEST"
                },
                {
                    "source": "alb_US_WEST",
                    "target": "cache_l2_US_WEST"
                },
                {
                    "source": "alb_US_WEST",
                    "target": "api_core_US_WEST"
                },
                {
                    "source": "client_EU",
                    "target": "dns_EU"
                },
                {
                    "source": "dns_EU",
                    "target": "cdn_EU_1"
                },
                {
                    "source": "dns_EU",
                    "target": "cdn_EU_2"
                },
                {
                    "source": "cdn_EU_1",
                    "target": "alb_EU"
                },
                {
                    "source": "cdn_EU_2",
                    "target": "alb_EU"
                },
                {
                    "source": "alb_EU",
                    "target": "cache_l2_EU"
                },
                {
                    "source": "alb_EU",
                    "target": "api_core_EU"
                },
                {
                    "source": "client_ASIA",
                    "target": "dns_ASIA"
                },
                {
                    "source": "dns_ASIA",
                    "target": "cdn_ASIA_1"
                },
                {
                    "source": "dns_ASIA",
                    "target": "cdn_ASIA_2"
                },
                {
                    "source": "cdn_ASIA_1",
                    "target": "alb_ASIA"
                },
                {
                    "source": "cdn_ASIA_2",
                    "target": "alb_ASIA"
                },
                {
                    "source": "alb_ASIA",
                    "target": "cache_l2_ASIA"
                },
                {
                    "source": "alb_ASIA",
                    "target": "api_core_ASIA"
                },
                {
                    "source": "client_SA",
                    "target": "dns_SA"
                },
                {
                    "source": "dns_SA",
                    "target": "cdn_SA_1"
                },
                {
                    "source": "dns_SA",
                    "target": "cdn_SA_2"
                },
                {
                    "source": "cdn_SA_1",
                    "target": "alb_SA"
                },
                {
                    "source": "cdn_SA_2",
                    "target": "alb_SA"
                },
                {
                    "source": "alb_SA",
                    "target": "cache_l2_SA"
                },
                {
                    "source": "alb_SA",
                    "target": "api_core_SA"
                },
                {
                    "source": "api_core_US_EAST",
                    "target": "auth_lb"
                },
                {
                    "source": "api_core_US_WEST",
                    "target": "auth_lb"
                },
                {
                    "source": "api_core_EU",
                    "target": "auth_lb"
                },
                {
                    "source": "api_core_ASIA",
                    "target": "auth_lb"
                },
                {
                    "source": "api_core_SA",
                    "target": "auth_lb"
                },
                {
                    "source": "auth_lb",
                    "target": "auth_svc_0"
                },
                {
                    "source": "auth_svc_0",
                    "target": "db_auth_master"
                },
                {
                    "source": "auth_lb",
                    "target": "auth_svc_1"
                },
                {
                    "source": "auth_svc_1",
                    "target": "db_auth_master"
                },
                {
                    "source": "auth_lb",
                    "target": "auth_svc_2"
                },
                {
                    "source": "auth_svc_2",
                    "target": "db_auth_master"
                },
                {
                    "source": "auth_lb",
                    "target": "auth_svc_3"
                },
                {
                    "source": "auth_svc_3",
                    "target": "db_auth_master"
                },
                {
                    "source": "auth_lb",
                    "target": "auth_svc_4"
                },
                {
                    "source": "auth_svc_4",
                    "target": "db_auth_master"
                },
                {
                    "source": "db_auth_master",
                    "target": "db_auth_replica_1"
                },
                {
                    "source": "db_auth_master",
                    "target": "db_auth_replica_2"
                },
                {
                    "source": "api_core_US_EAST",
                    "target": "catalog_lb"
                },
                {
                    "source": "api_core_US_WEST",
                    "target": "catalog_lb"
                },
                {
                    "source": "api_core_EU",
                    "target": "catalog_lb"
                },
                {
                    "source": "api_core_ASIA",
                    "target": "catalog_lb"
                },
                {
                    "source": "api_core_SA",
                    "target": "catalog_lb"
                },
                {
                    "source": "catalog_lb",
                    "target": "cat_svc_0"
                },
                {
                    "source": "cat_svc_0",
                    "target": "cache_global_cat"
                },
                {
                    "source": "catalog_lb",
                    "target": "cat_svc_1"
                },
                {
                    "source": "cat_svc_1",
                    "target": "cache_global_cat"
                },
                {
                    "source": "catalog_lb",
                    "target": "cat_svc_2"
                },
                {
                    "source": "cat_svc_2",
                    "target": "cache_global_cat"
                },
                {
                    "source": "catalog_lb",
                    "target": "cat_svc_3"
                },
                {
                    "source": "cat_svc_3",
                    "target": "cache_global_cat"
                },
                {
                    "source": "catalog_lb",
                    "target": "cat_svc_4"
                },
                {
                    "source": "cat_svc_4",
                    "target": "cache_global_cat"
                },
                {
                    "source": "catalog_lb",
                    "target": "cat_svc_5"
                },
                {
                    "source": "cat_svc_5",
                    "target": "cache_global_cat"
                },
                {
                    "source": "cache_global_cat",
                    "target": "db_catalog"
                },
                {
                    "source": "catalog_lb",
                    "target": "media_mq"
                },
                {
                    "source": "media_mq",
                    "target": "encoder_0"
                },
                {
                    "source": "encoder_0",
                    "target": "s3_archive"
                },
                {
                    "source": "media_mq",
                    "target": "encoder_1"
                },
                {
                    "source": "encoder_1",
                    "target": "s3_archive"
                },
                {
                    "source": "media_mq",
                    "target": "encoder_2"
                },
                {
                    "source": "encoder_2",
                    "target": "s3_archive"
                },
                {
                    "source": "media_mq",
                    "target": "encoder_3"
                },
                {
                    "source": "encoder_3",
                    "target": "s3_archive"
                },
                {
                    "source": "media_mq",
                    "target": "encoder_4"
                },
                {
                    "source": "encoder_4",
                    "target": "s3_archive"
                },
                {
                    "source": "media_mq",
                    "target": "encoder_5"
                },
                {
                    "source": "encoder_5",
                    "target": "s3_archive"
                },
                {
                    "source": "media_mq",
                    "target": "encoder_6"
                },
                {
                    "source": "encoder_6",
                    "target": "s3_archive"
                },
                {
                    "source": "media_mq",
                    "target": "encoder_7"
                },
                {
                    "source": "encoder_7",
                    "target": "s3_archive"
                }
            ]
        }
    },
    {
        "id": "template_legendary_fleet",
        "name": "Global IoT Telemetry (Legendary - 53 nodes)",
        "description": "Uber/Tesla style ingestion architecture featuring MQTT bridges, Kafka meshing, and Cassandra rings.",
        "graph": {
            "nodes": {
                "fleet_0": {
                    "label": "Vehicle Fleet 0",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 100
                    }
                },
                "nlb_0": {
                    "label": "TCP Ingress 0",
                    "type": "load_balancer",
                    "capacity": 25000,
                    "position": {
                        "x": 300,
                        "y": 150
                    }
                },
                "fleet_1": {
                    "label": "Vehicle Fleet 1",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 200
                    }
                },
                "fleet_2": {
                    "label": "Vehicle Fleet 2",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 300
                    }
                },
                "nlb_1": {
                    "label": "TCP Ingress 1",
                    "type": "load_balancer",
                    "capacity": 25000,
                    "position": {
                        "x": 300,
                        "y": 350
                    }
                },
                "fleet_3": {
                    "label": "Vehicle Fleet 3",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 400
                    }
                },
                "fleet_4": {
                    "label": "Vehicle Fleet 4",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 500
                    }
                },
                "nlb_2": {
                    "label": "TCP Ingress 2",
                    "type": "load_balancer",
                    "capacity": 25000,
                    "position": {
                        "x": 300,
                        "y": 550
                    }
                },
                "fleet_5": {
                    "label": "Vehicle Fleet 5",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 600
                    }
                },
                "fleet_6": {
                    "label": "Vehicle Fleet 6",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 700
                    }
                },
                "nlb_3": {
                    "label": "TCP Ingress 3",
                    "type": "load_balancer",
                    "capacity": 25000,
                    "position": {
                        "x": 300,
                        "y": 750
                    }
                },
                "fleet_7": {
                    "label": "Vehicle Fleet 7",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 800
                    }
                },
                "fleet_8": {
                    "label": "Vehicle Fleet 8",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 900
                    }
                },
                "nlb_4": {
                    "label": "TCP Ingress 4",
                    "type": "load_balancer",
                    "capacity": 25000,
                    "position": {
                        "x": 300,
                        "y": 950
                    }
                },
                "fleet_9": {
                    "label": "Vehicle Fleet 9",
                    "type": "client",
                    "base_rps": 8000,
                    "position": {
                        "x": 100,
                        "y": 1000
                    }
                },
                "mqtt_0": {
                    "label": "MQTT Broker 0",
                    "type": "api_server",
                    "capacity": 20000,
                    "position": {
                        "x": 500,
                        "y": 150
                    }
                },
                "mqtt_1": {
                    "label": "MQTT Broker 1",
                    "type": "api_server",
                    "capacity": 20000,
                    "position": {
                        "x": 500,
                        "y": 350
                    }
                },
                "mqtt_2": {
                    "label": "MQTT Broker 2",
                    "type": "api_server",
                    "capacity": 20000,
                    "position": {
                        "x": 500,
                        "y": 550
                    }
                },
                "mqtt_3": {
                    "label": "MQTT Broker 3",
                    "type": "api_server",
                    "capacity": 20000,
                    "position": {
                        "x": 500,
                        "y": 750
                    }
                },
                "mqtt_4": {
                    "label": "MQTT Broker 4",
                    "type": "api_server",
                    "capacity": 20000,
                    "position": {
                        "x": 500,
                        "y": 950
                    }
                },
                "kafka_part_0": {
                    "label": "Kafka Partition 0",
                    "type": "message_queue",
                    "capacity": 30000,
                    "position": {
                        "x": 750,
                        "y": 200
                    }
                },
                "flink_0_0": {
                    "label": "Stream Proc 0-0",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 180
                    }
                },
                "cassandra_0": {
                    "label": "Cassandra Node 0",
                    "type": "database",
                    "write_capacity": 25000,
                    "position": {
                        "x": 1250,
                        "y": 200
                    }
                },
                "redis_geo_0": {
                    "label": "GeoState Cache 0",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 1250,
                        "y": 150
                    }
                },
                "flink_0_1": {
                    "label": "Stream Proc 0-1",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 230
                    }
                },
                "kafka_part_1": {
                    "label": "Kafka Partition 1",
                    "type": "message_queue",
                    "capacity": 30000,
                    "position": {
                        "x": 750,
                        "y": 320
                    }
                },
                "flink_1_0": {
                    "label": "Stream Proc 1-0",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 300
                    }
                },
                "cassandra_1": {
                    "label": "Cassandra Node 1",
                    "type": "database",
                    "write_capacity": 25000,
                    "position": {
                        "x": 1250,
                        "y": 320
                    }
                },
                "redis_geo_1": {
                    "label": "GeoState Cache 1",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 1250,
                        "y": 270
                    }
                },
                "flink_1_1": {
                    "label": "Stream Proc 1-1",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 350
                    }
                },
                "kafka_part_2": {
                    "label": "Kafka Partition 2",
                    "type": "message_queue",
                    "capacity": 30000,
                    "position": {
                        "x": 750,
                        "y": 440
                    }
                },
                "flink_2_0": {
                    "label": "Stream Proc 2-0",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 420
                    }
                },
                "cassandra_2": {
                    "label": "Cassandra Node 2",
                    "type": "database",
                    "write_capacity": 25000,
                    "position": {
                        "x": 1250,
                        "y": 440
                    }
                },
                "redis_geo_2": {
                    "label": "GeoState Cache 2",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 1250,
                        "y": 390
                    }
                },
                "flink_2_1": {
                    "label": "Stream Proc 2-1",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 470
                    }
                },
                "kafka_part_3": {
                    "label": "Kafka Partition 3",
                    "type": "message_queue",
                    "capacity": 30000,
                    "position": {
                        "x": 750,
                        "y": 560
                    }
                },
                "flink_3_0": {
                    "label": "Stream Proc 3-0",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 540
                    }
                },
                "cassandra_3": {
                    "label": "Cassandra Node 3",
                    "type": "database",
                    "write_capacity": 25000,
                    "position": {
                        "x": 1250,
                        "y": 560
                    }
                },
                "redis_geo_3": {
                    "label": "GeoState Cache 3",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 1250,
                        "y": 510
                    }
                },
                "flink_3_1": {
                    "label": "Stream Proc 3-1",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 590
                    }
                },
                "kafka_part_4": {
                    "label": "Kafka Partition 4",
                    "type": "message_queue",
                    "capacity": 30000,
                    "position": {
                        "x": 750,
                        "y": 680
                    }
                },
                "flink_4_0": {
                    "label": "Stream Proc 4-0",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 660
                    }
                },
                "cassandra_4": {
                    "label": "Cassandra Node 4",
                    "type": "database",
                    "write_capacity": 25000,
                    "position": {
                        "x": 1250,
                        "y": 680
                    }
                },
                "redis_geo_4": {
                    "label": "GeoState Cache 4",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 1250,
                        "y": 630
                    }
                },
                "flink_4_1": {
                    "label": "Stream Proc 4-1",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 710
                    }
                },
                "kafka_part_5": {
                    "label": "Kafka Partition 5",
                    "type": "message_queue",
                    "capacity": 30000,
                    "position": {
                        "x": 750,
                        "y": 800
                    }
                },
                "flink_5_0": {
                    "label": "Stream Proc 5-0",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 780
                    }
                },
                "cassandra_5": {
                    "label": "Cassandra Node 5",
                    "type": "database",
                    "write_capacity": 25000,
                    "position": {
                        "x": 1250,
                        "y": 800
                    }
                },
                "redis_geo_5": {
                    "label": "GeoState Cache 5",
                    "type": "cache",
                    "capacity": 20000,
                    "position": {
                        "x": 1250,
                        "y": 750
                    }
                },
                "flink_5_1": {
                    "label": "Stream Proc 5-1",
                    "type": "worker",
                    "capacity": 15000,
                    "position": {
                        "x": 1000,
                        "y": 830
                    }
                }
            },
            "edges": [
                {
                    "source": "fleet_0",
                    "target": "nlb_0"
                },
                {
                    "source": "fleet_1",
                    "target": "nlb_0"
                },
                {
                    "source": "fleet_2",
                    "target": "nlb_1"
                },
                {
                    "source": "fleet_3",
                    "target": "nlb_1"
                },
                {
                    "source": "fleet_4",
                    "target": "nlb_2"
                },
                {
                    "source": "fleet_5",
                    "target": "nlb_2"
                },
                {
                    "source": "fleet_6",
                    "target": "nlb_3"
                },
                {
                    "source": "fleet_7",
                    "target": "nlb_3"
                },
                {
                    "source": "fleet_8",
                    "target": "nlb_4"
                },
                {
                    "source": "fleet_9",
                    "target": "nlb_4"
                },
                {
                    "source": "nlb_0",
                    "target": "mqtt_0"
                },
                {
                    "source": "mqtt_0",
                    "target": "kafka_part_0"
                },
                {
                    "source": "mqtt_0",
                    "target": "kafka_part_1"
                },
                {
                    "source": "mqtt_0",
                    "target": "kafka_part_2"
                },
                {
                    "source": "nlb_1",
                    "target": "mqtt_1"
                },
                {
                    "source": "mqtt_1",
                    "target": "kafka_part_0"
                },
                {
                    "source": "mqtt_1",
                    "target": "kafka_part_1"
                },
                {
                    "source": "mqtt_1",
                    "target": "kafka_part_2"
                },
                {
                    "source": "nlb_2",
                    "target": "mqtt_2"
                },
                {
                    "source": "mqtt_2",
                    "target": "kafka_part_0"
                },
                {
                    "source": "mqtt_2",
                    "target": "kafka_part_1"
                },
                {
                    "source": "mqtt_2",
                    "target": "kafka_part_2"
                },
                {
                    "source": "nlb_3",
                    "target": "mqtt_3"
                },
                {
                    "source": "mqtt_3",
                    "target": "kafka_part_0"
                },
                {
                    "source": "mqtt_3",
                    "target": "kafka_part_1"
                },
                {
                    "source": "mqtt_3",
                    "target": "kafka_part_2"
                },
                {
                    "source": "nlb_4",
                    "target": "mqtt_4"
                },
                {
                    "source": "mqtt_4",
                    "target": "kafka_part_0"
                },
                {
                    "source": "mqtt_4",
                    "target": "kafka_part_1"
                },
                {
                    "source": "mqtt_4",
                    "target": "kafka_part_2"
                },
                {
                    "source": "kafka_part_0",
                    "target": "flink_0_0"
                },
                {
                    "source": "flink_0_0",
                    "target": "cassandra_0"
                },
                {
                    "source": "flink_0_0",
                    "target": "redis_geo_0"
                },
                {
                    "source": "kafka_part_0",
                    "target": "flink_0_1"
                },
                {
                    "source": "flink_0_1",
                    "target": "cassandra_0"
                },
                {
                    "source": "flink_0_1",
                    "target": "redis_geo_0"
                },
                {
                    "source": "kafka_part_1",
                    "target": "flink_1_0"
                },
                {
                    "source": "flink_1_0",
                    "target": "cassandra_1"
                },
                {
                    "source": "flink_1_0",
                    "target": "redis_geo_1"
                },
                {
                    "source": "kafka_part_1",
                    "target": "flink_1_1"
                },
                {
                    "source": "flink_1_1",
                    "target": "cassandra_1"
                },
                {
                    "source": "flink_1_1",
                    "target": "redis_geo_1"
                },
                {
                    "source": "kafka_part_2",
                    "target": "flink_2_0"
                },
                {
                    "source": "flink_2_0",
                    "target": "cassandra_2"
                },
                {
                    "source": "flink_2_0",
                    "target": "redis_geo_2"
                },
                {
                    "source": "kafka_part_2",
                    "target": "flink_2_1"
                },
                {
                    "source": "flink_2_1",
                    "target": "cassandra_2"
                },
                {
                    "source": "flink_2_1",
                    "target": "redis_geo_2"
                },
                {
                    "source": "kafka_part_3",
                    "target": "flink_3_0"
                },
                {
                    "source": "flink_3_0",
                    "target": "cassandra_3"
                },
                {
                    "source": "flink_3_0",
                    "target": "redis_geo_3"
                },
                {
                    "source": "kafka_part_3",
                    "target": "flink_3_1"
                },
                {
                    "source": "flink_3_1",
                    "target": "cassandra_3"
                },
                {
                    "source": "flink_3_1",
                    "target": "redis_geo_3"
                },
                {
                    "source": "kafka_part_4",
                    "target": "flink_4_0"
                },
                {
                    "source": "flink_4_0",
                    "target": "cassandra_4"
                },
                {
                    "source": "flink_4_0",
                    "target": "redis_geo_4"
                },
                {
                    "source": "kafka_part_4",
                    "target": "flink_4_1"
                },
                {
                    "source": "flink_4_1",
                    "target": "cassandra_4"
                },
                {
                    "source": "flink_4_1",
                    "target": "redis_geo_4"
                },
                {
                    "source": "kafka_part_5",
                    "target": "flink_5_0"
                },
                {
                    "source": "flink_5_0",
                    "target": "cassandra_5"
                },
                {
                    "source": "flink_5_0",
                    "target": "redis_geo_5"
                },
                {
                    "source": "kafka_part_5",
                    "target": "flink_5_1"
                },
                {
                    "source": "flink_5_1",
                    "target": "cassandra_5"
                },
                {
                    "source": "flink_5_1",
                    "target": "redis_geo_5"
                },
                {
                    "source": "cassandra_0",
                    "target": "cassandra_1"
                },
                {
                    "source": "cassandra_1",
                    "target": "cassandra_2"
                },
                {
                    "source": "cassandra_2",
                    "target": "cassandra_3"
                },
                {
                    "source": "cassandra_3",
                    "target": "cassandra_4"
                },
                {
                    "source": "cassandra_4",
                    "target": "cassandra_5"
                },
                {
                    "source": "cassandra_5",
                    "target": "cassandra_0"
                }
            ]
        }
    }
]
