def get_templates():
    return [
        {
            "id": "template_small",
            "name": "Static Blog (Small - 4 nodes)",
            "description": "Basic global static site hosting pipeline.",
            "graph": {
                 "nodes": {
                     "client_1": { "label": "Global Users", "type": "client", "base_rps": 500, "position": {"x": 100, "y": 200} },
                     "dns_1": { "label": "Route53", "type": "dns", "capacity": 50000, "position": {"x": 350, "y": 200} },
                     "cdn_1": { "label": "CloudFront CDN", "type": "cdn", "capacity": 20000, "position": {"x": 600, "y": 200} },
                     "obj_1": { "label": "S3 Content", "type": "object_store", "capacity": 1000, "position": {"x": 850, "y": 200} }
                 },
                 "edges": [
                     {"source": "client_1", "target": "dns_1"},
                     {"source": "dns_1", "target": "cdn_1"},
                     {"source": "cdn_1", "target": "obj_1"}
                 ]
            }
        },
        {
            "id": "template_medium_ecom",
            "name": "E-commerce (Medium - 8 nodes)",
            "description": "Standard checkout architecture.",
            "graph": {
                 "nodes": {
                     "client_1": { "label": "Shoppers", "type": "client", "base_rps": 1500, "position": {"x": 100, "y": 250} },
                     "dns_1": { "label": "DNS Entry", "type": "dns", "capacity": 50000, "position": {"x": 300, "y": 250} },
                     "waf_1": { "label": "WAF & Security", "type": "load_balancer", "capacity": 10000, "position": {"x": 500, "y": 250} },
                     "alb_1": { "label": "Core Gateway", "type": "load_balancer", "capacity": 6000, "position": {"x": 700, "y": 250} },
                     "api_web": { "label": "Frontend API", "type": "api_server", "capacity": 2000, "position": {"x": 900, "y": 150} },
                     "api_pay": { "label": "Payment API", "type": "api_server", "capacity": 800, "position": {"x": 900, "y": 350} },
                     "cache_1": { "label": "Session Cache", "type": "cache", "capacity": 5000, "position": {"x": 1150, "y": 150} },
                     "db_1": { "label": "Transactions DB", "type": "database", "write_capacity": 1000, "position": {"x": 1150, "y": 350} }
                 },
                 "edges": [
                     {"source": "client_1", "target": "dns_1"},
                     {"source": "dns_1", "target": "waf_1"},
                     {"source": "waf_1", "target": "alb_1"},
                     {"source": "alb_1", "target": "api_web"},
                     {"source": "alb_1", "target": "api_pay"},
                     {"source": "api_web", "target": "cache_1"},
                     {"source": "api_pay", "target": "db_1"}
                 ]
            }
        },
        {
            "id": "template_medium_chat",
            "name": "PubSub Chat (Medium - 8 nodes)",
            "description": "Real-time socket communication.",
            "graph": {
                 "nodes": {
                     "client_1": { "label": "Mobile Users", "type": "client", "base_rps": 2500, "position": {"x": 50, "y": 250} },
                     "alb_1": { "label": "Ingress LB", "type": "load_balancer", "capacity": 15000, "position": {"x": 250, "y": 250} },
                     "api_auth": { "label": "Auth API", "type": "api_server", "capacity": 3000, "position": {"x": 450, "y": 150} },
                     "api_soc": { "label": "Socket Node", "type": "api_server", "capacity": 5000, "position": {"x": 450, "y": 350} },
                     "mq_1": { "label": "Kafka Broker", "type": "message_queue", "capacity": 20000, "position": {"x": 700, "y": 350} },
                     "work_1": { "label": "Delivery Worker", "type": "worker", "capacity": 2000, "position": {"x": 950, "y": 250} },
                     "cache_1": { "label": "Presence Redis", "type": "cache", "capacity": 8000, "position": {"x": 700, "y": 150} },
                     "db_1": { "label": "Messages DB", "type": "database", "write_capacity": 1500, "position": {"x": 1200, "y": 250} }
                 },
                 "edges": [
                     {"source": "client_1", "target": "alb_1"},
                     {"source": "alb_1", "target": "api_auth"},
                     {"source": "alb_1", "target": "api_soc"},
                     {"source": "api_auth", "target": "cache_1"},
                     {"source": "api_soc", "target": "mq_1"},
                     {"source": "mq_1", "target": "work_1"},
                     {"source": "work_1", "target": "db_1"}
                 ]
            }
        },
        {
            "id": "template_dense_media",
            "name": "Global Media (Dense - 12 nodes)",
            "description": "High read-throughput platform.",
            "graph": {
                 "nodes": {
                     "c_mob": { "label": "Mobile App", "type": "client", "base_rps": 6000, "position": {"x": 50, "y": 150} },
                     "c_web": { "label": "Web Browsers", "type": "client", "base_rps": 4000, "position": {"x": 50, "y": 350} },
                     "dns_1": { "label": "Global DNS", "type": "dns", "capacity": 50000, "position": {"x": 250, "y": 250} },
                     "cdn_eu": { "label": "EU Edge CDN", "type": "cdn", "capacity": 15000, "position": {"x": 450, "y": 150} },
                     "cdn_us": { "label": "US Edge CDN", "type": "cdn", "capacity": 20000, "position": {"x": 450, "y": 350} },
                     "lb_origin": { "label": "Origin ALB", "type": "load_balancer", "capacity": 8000, "position": {"x": 650, "y": 250} },
                     "api_vid": { "label": "Video Router API", "type": "api_server", "capacity": 2000, "position": {"x": 850, "y": 150} },
                     "api_usr": { "label": "User Info API", "type": "api_server", "capacity": 1500, "position": {"x": 850, "y": 350} },
                     "cache_l1": { "label": "L1 Redis", "type": "cache", "capacity": 10000, "position": {"x": 1050, "y": 50} },
                     "cache_l2": { "label": "L2 Memcache", "type": "cache", "capacity": 8000, "position": {"x": 1050, "y": 250} },
                     "s3_cold": { "label": "Blob Storage", "type": "object_store", "capacity": 3000, "position": {"x": 1250, "y": 150} },
                     "db_meta": { "label": "User DB Primary", "type": "database", "write_capacity": 1000, "position": {"x": 1050, "y": 450} }
                 },
                 "edges": [
                     {"source": "c_mob", "target": "dns_1"},
                     {"source": "c_web", "target": "dns_1"},
                     {"source": "dns_1", "target": "cdn_eu"},
                     {"source": "dns_1", "target": "cdn_us"},
                     {"source": "cdn_eu", "target": "lb_origin"},
                     {"source": "cdn_us", "target": "lb_origin"},
                     {"source": "lb_origin", "target": "api_vid"},
                     {"source": "lb_origin", "target": "api_usr"},
                     {"source": "api_vid", "target": "cache_l1"},
                     {"source": "cache_l1", "target": "cache_l2"},
                     {"source": "cache_l2", "target": "s3_cold"},
                     {"source": "api_usr", "target": "db_meta"}
                 ]
            }
        },
        {
            "id": "template_extreme_fintech",
            "name": "Global FinTech (Extreme - 20 nodes)",
            "description": "Massive scale microservices architecture.",
            "graph": {
                 "nodes": {
                     "c_mob": { "label": "Mobile Apps", "type": "client", "base_rps": 2000, "position": {"x": 50, "y": 150} },
                     "c_web": { "label": "Web Portal", "type": "client", "base_rps": 1500, "position": {"x": 50, "y": 300} },
                     "c_b2b": { "label": "B2B API Partners", "type": "client", "base_rps": 800, "position": {"x": 50, "y": 450} },
                     
                     "dns": { "label": "Global DNS", "type": "dns", "capacity": 100000, "position": {"x": 250, "y": 300} },
                     "cdn": { "label": "Edge Accelerator", "type": "cdn", "capacity": 50000, "position": {"x": 450, "y": 225} },
                     "waf": { "label": "DDoS Shield", "type": "load_balancer", "capacity": 30000, "position": {"x": 450, "y": 375} },
                     
                     "api_gw": { "label": "API Gateway", "type": "api_server", "capacity": 15000, "position": {"x": 650, "y": 300} },
                     
                     "auth_svc": { "label": "Auth Service", "type": "serverless", "capacity": 5000, "position": {"x": 850, "y": 100} },
                     "ledger_svc": { "label": "Ledger Service", "type": "api_server", "capacity": 3000, "position": {"x": 850, "y": 300} },
                     "trade_svc": { "label": "Trading Engine", "type": "api_server", "capacity": 1500, "position": {"x": 850, "y": 500} },
                     "report_svc": { "label": "Report Service", "type": "serverless", "capacity": 2000, "position": {"x": 850, "y": 700} },
                     
                     "cache_auth": { "label": "Session Redis", "type": "cache", "capacity": 15000, "position": {"x": 1050, "y": 100} },
                     
                     "mq_trades": { "label": "Kafka Trades", "type": "message_queue", "capacity": 25000, "position": {"x": 1050, "y": 500} },
                     
                     "work_match": { "label": "Matcher Worker", "type": "worker", "capacity": 800, "position": {"x": 1250, "y": 400} },
                     "work_risk": { "label": "Risk Analyzer", "type": "worker", "capacity": 500, "position": {"x": 1250, "y": 500} },
                     "work_audit": { "label": "Audit Crawler", "type": "worker", "capacity": 600, "position": {"x": 1250, "y": 600} },
                     
                     "db_ledger": { "label": "Hot Ledger DB", "type": "database", "write_capacity": 5000, "position": {"x": 1500, "y": 300} },
                     "db_trades": { "label": "Raw Trades DB", "type": "database", "write_capacity": 3000, "position": {"x": 1500, "y": 500} },
                     "db_archive": { "label": "Slow Archive DB", "type": "database", "write_capacity": 500, "position": {"x": 1500, "y": 700} },
                     "s3_blob": { "label": "Statement Blob", "type": "object_store", "capacity": 2000, "position": {"x": 1250, "y": 700} }
                 },
                 "edges": [
                     {"source": "c_mob", "target": "dns"},
                     {"source": "c_web", "target": "dns"},
                     {"source": "c_b2b", "target": "dns"},
                     {"source": "dns", "target": "cdn"},
                     {"source": "dns", "target": "waf"},
                     {"source": "cdn", "target": "api_gw"},
                     {"source": "waf", "target": "api_gw"},
                     
                     {"source": "api_gw", "target": "auth_svc"},
                     {"source": "api_gw", "target": "ledger_svc"},
                     {"source": "api_gw", "target": "trade_svc"},
                     {"source": "api_gw", "target": "report_svc"},
                     
                     {"source": "auth_svc", "target": "cache_auth"},
                     
                     {"source": "ledger_svc", "target": "db_ledger"},
                     
                     {"source": "trade_svc", "target": "mq_trades"},
                     {"source": "mq_trades", "target": "work_match"},
                     {"source": "mq_trades", "target": "work_risk"},
                     {"source": "mq_trades", "target": "work_audit"},
                     
                     {"source": "work_match", "target": "db_ledger"},
                     {"source": "work_match", "target": "db_trades"},
                     {"source": "work_risk", "target": "db_trades"},
                     {"source": "work_audit", "target": "db_archive"},
                     
                     {"source": "report_svc", "target": "db_archive"},
                     {"source": "report_svc", "target": "s3_blob"}
                 ]
            }
        }
    ]
