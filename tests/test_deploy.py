import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch, MagicMock

spec=importlib.util.spec_from_file_location('deploy',Path(__file__).resolve().parents[1]/'scripts/deploy_hetzner.py')
deploy=importlib.util.module_from_spec(spec);spec.loader.exec_module(deploy)

class DeployTests(TestCase):
    config={'HETZNER_HOST':'example.org','HETZNER_USER':'test','HETZNER_PASSWORD':' test ','HETZNER_MENU_DIR':'/public_html/menu'}
    def test_root_and_traversal_rejected(self):
        for target in ['/', '/public_html', '/public_html/../other', 'menu']:
            with patch.dict('os.environ',dict(self.config,HETZNER_MENU_DIR=target)):
                with self.assertRaises(ValueError):deploy.settings()
    def test_password_preserved(self):
        with patch.dict('os.environ',self.config):
            self.assertEqual(deploy.settings()['PASSWORD'],' test ')
    def test_tls_upload_and_no_deletion(self):
        ftp=MagicMock();ftp.__enter__.return_value=ftp;ftp.pwd.return_value='/public_html/menu'
        with TemporaryDirectory() as directory:
            root=Path(directory);(root/'_site/admin').mkdir(parents=True)
            for name in ['index.html','admin/index.html','admin/config.yml','style.css']:
                (root/'_site'/name).write_text('fixture',encoding='utf-8')
            with patch.dict('os.environ',self.config), patch.object(deploy,'__file__',str(root/'scripts/deploy_hetzner.py')), patch.object(deploy,'FTP_TLS',return_value=ftp) as factory:
                deploy.deploy()
        self.assertTrue(factory.call_args.kwargs['context'].check_hostname)
        ftp.prot_p.assert_called_once()
        ftp.delete.assert_not_called();ftp.rmd.assert_not_called()
        names=[call.args[0] for call in ftp.storbinary.call_args_list]
        self.assertIn('STOR config.yml',names)
        self.assertTrue(names[-1].endswith('.html'))
        first_html=next(i for i,n in enumerate(names) if n.endswith('.html'))
        self.assertTrue(all(n.endswith('.html') for n in names[first_html:]))
